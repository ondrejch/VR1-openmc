"""Reusable VR-1 digital twin helpers.

This module factors the notebook's final ROM cell into importable functions.
It trains the k-effective surrogate and the POD-based flux surrogate from the
precomputed VR-1 data sets, then exposes batch prediction helpers that return
reactivity and flattened flux vectors for arbitrary parameter arrays.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn import ensemble
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


FEATURE_COLUMNS: tuple[str, ...] = (
    "cr1_height",
    "cr2_height",
    "dummy_water_density_multiplier",
    "fuel_assembly_water_density_multiplier",
)

MESH_SHAPE: tuple[int, int, int, int] = (70, 60, 60, 2)
THERMAL_FAST_FLUX_SIZE = int(np.prod(MESH_SHAPE))


@dataclass(frozen=True)
class DigitalTwinBundle:
    """Trained models and reduced basis for the VR-1 digital twin."""

    data_root: Path
    n_modes: int
    keff_model: Any
    flux_model: Any
    pod_basis: np.ndarray
    singular_values: np.ndarray


def _resolve_data_root(data_root: str | Path | None) -> Path:
    if data_root is None:
        return Path(__file__).resolve().parent
    return Path(data_root)


def _training_csv_path(data_root: Path) -> Path:
    return data_root / "VR1_DT_Lab_Training_Data" / "training_set.csv"


def _test_csv_path(data_root: Path) -> Path:
    return data_root / "VR1_DT_Lab_Test_Data" / "test_set.csv"


def _training_data_dir(data_root: Path) -> Path:
    return data_root / "VR1_DT_Lab_Training_Data"


def _case_file_path(folder: Path, case_id: int) -> Path:
    return folder / f"results_case_{int(case_id)}.npz"


def load_parameter_frame(csv_path: str | Path) -> pd.DataFrame:
    """Load a VR-1 parameter CSV such as training_set.csv or test_set.csv."""

    return pd.read_csv(csv_path)


def load_flux_data(file_path: str | Path) -> np.ndarray:
    """Load one NPZ file and reconstruct the thermal/fast 4D flux field."""

    with np.load(file_path) as data:
        thermal = data["thermal_flux"]
        fast = data["fast_flux"]

    thermal_3d = thermal.reshape(MESH_SHAPE[:3])
    fast_3d = fast.reshape(MESH_SHAPE[:3])
    return np.stack([thermal_3d, fast_3d], axis=-1)


def flatten_flux_field(flux_field: np.ndarray) -> np.ndarray:
    """Flatten a 4D flux field into the vector layout used by the ROM."""

    return np.asarray(flux_field, dtype=float).reshape(-1)


def reshape_flux_vector(flux_vector: np.ndarray) -> np.ndarray:
    """Restore a flattened flux vector to the original 4D mesh layout."""

    return np.asarray(flux_vector, dtype=float).reshape(MESH_SHAPE)


def extract_keff(dataframe: pd.DataFrame, folder_path: str | Path) -> np.ndarray:
    """Extract the OpenMC k-effective values for each case in a parameter table."""

    folder = Path(folder_path)
    keff_values: list[float] = []

    for case_id in dataframe["case_id"]:
        file_path = _case_file_path(folder, int(case_id))
        with np.load(file_path) as data:
            keff_values.append(float(data["keff"]))

    return np.asarray(keff_values, dtype=float)


def build_snapshot_matrix(dataframe: pd.DataFrame, folder_path: str | Path) -> np.ndarray:
    """Assemble the flattened flux snapshots into a column-major matrix."""

    folder = Path(folder_path)
    snapshots: list[np.ndarray] = []

    for case_id in dataframe["case_id"]:
        flux_field = load_flux_data(_case_file_path(folder, int(case_id)))
        snapshots.append(flatten_flux_field(flux_field))

    return np.column_stack(snapshots)


def make_keff_model(model_kind: str = "random_forest") -> Any:
    """Construct the k-effective regression model used by the digital twin."""

    if model_kind == "linear":
        return LinearRegression()
    if model_kind == "polynomial":
        return make_pipeline(PolynomialFeatures(degree=3), LinearRegression())
    if model_kind == "random_forest":
        return ensemble.RandomForestRegressor(n_estimators=100, random_state=42)
    raise ValueError(f"Unsupported keff model kind: {model_kind}")


def make_flux_model(model_kind: str = "random_forest") -> Any:
    """Construct the flux-coefficient regression model used by the digital twin."""

    return make_keff_model(model_kind)


def fit_digital_twin(
    data_root: str | Path | None = None,
    n_modes: int = 10,
    keff_model_kind: str = "random_forest",
    flux_model_kind: str = "random_forest",
) -> DigitalTwinBundle:
    """Train the k-effective and flux ROM models from the saved VR-1 data."""

    resolved_root = _resolve_data_root(data_root)
    train_df = load_parameter_frame(_training_csv_path(resolved_root))
    train_dir = _training_data_dir(resolved_root)

    x_train = train_df[list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    y_train_keff = extract_keff(train_df, train_dir)

    snapshot_matrix = build_snapshot_matrix(train_df, train_dir)
    u_matrix, singular_values, _ = np.linalg.svd(snapshot_matrix, full_matrices=False)
    pod_basis = u_matrix[:, :n_modes]

    modal_coefficients = pod_basis.T @ snapshot_matrix
    y_train_coeffs = modal_coefficients.T

    keff_model = make_keff_model(keff_model_kind)
    flux_model = make_flux_model(flux_model_kind)

    keff_model.fit(x_train, y_train_keff)
    flux_model.fit(x_train, y_train_coeffs)

    return DigitalTwinBundle(
        data_root=resolved_root,
        n_modes=n_modes,
        keff_model=keff_model,
        flux_model=flux_model,
        pod_basis=pod_basis,
        singular_values=singular_values,
    )


@lru_cache(maxsize=1)
def load_default_bundle(
    data_root: str | Path | None = None,
    n_modes: int = 10,
    keff_model_kind: str = "random_forest",
    flux_model_kind: str = "random_forest",
) -> DigitalTwinBundle:
    """Load and cache the default trained bundle for repeated predictions."""

    return fit_digital_twin(
        data_root=data_root,
        n_modes=n_modes,
        keff_model_kind=keff_model_kind,
        flux_model_kind=flux_model_kind,
    )


def _normalize_parameter_space(parameter_space: np.ndarray | list[list[float]] | list[float]) -> tuple[np.ndarray, bool]:
    values = np.asarray(parameter_space, dtype=float)
    if values.ndim == 1:
        if values.size != len(FEATURE_COLUMNS):
            raise ValueError(f"Expected {len(FEATURE_COLUMNS)} parameters per state, got {values.size}.")
        return values.reshape(1, -1), True

    if values.ndim != 2 or values.shape[1] != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Expected parameter_space with shape (n_samples, {len(FEATURE_COLUMNS)}); got {values.shape}."
        )

    return values, False


def predict_reactivity_and_flux(
    parameter_space: np.ndarray | list[list[float]] | list[float],
    bundle: DigitalTwinBundle | None = None,
    data_root: str | Path | None = None,
    n_modes: int = 10,
    keff_model_kind: str = "random_forest",
    flux_model_kind: str = "random_forest",
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Predict reactivity and flattened flux vectors for one or more states.

    The input may be a single 4-element parameter vector or an array with shape
    (n_samples, 4). The returned flux vectors are flattened in the same order as
    the notebook's snapshot matrix.
    """

    if bundle is None:
        bundle = load_default_bundle(
            data_root=data_root,
            n_modes=n_modes,
            keff_model_kind=keff_model_kind,
            flux_model_kind=flux_model_kind,
        )

    states, was_single_state = _normalize_parameter_space(parameter_space)

    keff = np.asarray(bundle.keff_model.predict(states), dtype=float)
    reactivity = (keff - 1.0) / keff

    coeffs = np.asarray(bundle.flux_model.predict(states), dtype=float)
    flux_vectors = coeffs @ bundle.pod_basis.T

    if was_single_state:
        return float(reactivity[0]), flux_vectors[0]

    return reactivity, flux_vectors


def predict_keff_and_flux(
    parameter_space: np.ndarray | list[list[float]] | list[float],
    bundle: DigitalTwinBundle | None = None,
    data_root: str | Path | None = None,
    n_modes: int = 10,
    keff_model_kind: str = "random_forest",
    flux_model_kind: str = "random_forest",
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Predict k-effective and flattened flux vectors for one or more states."""

    if bundle is None:
        bundle = load_default_bundle(
            data_root=data_root,
            n_modes=n_modes,
            keff_model_kind=keff_model_kind,
            flux_model_kind=flux_model_kind,
        )

    states, was_single_state = _normalize_parameter_space(parameter_space)

    keff = np.asarray(bundle.keff_model.predict(states), dtype=float)
    coeffs = np.asarray(bundle.flux_model.predict(states), dtype=float)
    flux_vectors = coeffs @ bundle.pod_basis.T

    if was_single_state:
        return float(keff[0]), flux_vectors[0]

    return keff, flux_vectors


def default_test_csv(data_root: str | Path | None = None) -> Path:
    """Return the expected test-set path for the current data root."""

    return _test_csv_path(_resolve_data_root(data_root))


def default_training_csv(data_root: str | Path | None = None) -> Path:
    """Return the expected training-set path for the current data root."""

    return _training_csv_path(_resolve_data_root(data_root))


__all__ = [
    "DigitalTwinBundle",
    "FEATURE_COLUMNS",
    "MESH_SHAPE",
    "THERMAL_FAST_FLUX_SIZE",
    "build_snapshot_matrix",
    "default_test_csv",
    "default_training_csv",
    "extract_keff",
    "fit_digital_twin",
    "flatten_flux_field",
    "load_default_bundle",
    "load_flux_data",
    "load_parameter_frame",
    "make_flux_model",
    "make_keff_model",
    "predict_keff_and_flux",
    "predict_reactivity_and_flux",
    "reshape_flux_vector",
]
