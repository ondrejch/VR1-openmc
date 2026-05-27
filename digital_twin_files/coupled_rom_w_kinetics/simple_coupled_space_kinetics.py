#!/usr/bin/env python3
"""Simple coupled point kinetics visualization for three local flux points.

This script keeps the time evolution intentionally small:
- use a standard point-kinetics solver,
- drive it with example-style reactivity insertions (step, ramp, sinusoidal),
- sample a nominal ROM flux shape once,
- and plot the resulting local thermal and fast flux histories at three points.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from digital_twin_files.rom.digital_twin import MESH_SHAPE
from digital_twin_files.rom.digital_twin import load_default_bundle
from digital_twin_files.rom.digital_twin import predict_reactivity_and_flux
from digital_twin_files.rom.digital_twin import reshape_flux_vector
from pke.solver import PointKineticsEquationSolver
from pke.solver import thermal_default_params


POINTS_OF_INTEREST: dict[str, tuple[int, int, int]] = {
    "Fuel": (35, 60, 60),
    "Near Control Rod": (35, 65, 82),
    "Moderator": (35, 65, 38),
}

TRANSIENT_MODES = ("step", "ramp", "sinusoidal")
THERMAL_GROUP = 0
FAST_GROUP = 1


def build_reactivity_function(
    transient: str,
    beta_total: float,
    step_onset: float,
    step_fraction: float,
    ramp_start: float,
    ramp_slope_fraction: float,
    sinusoidal_amplitude_fraction: float,
    sinusoidal_period: float,
):
    if transient == "step":
        return lambda t: float(step_fraction * beta_total if t >= step_onset else 0.0)
    if transient == "ramp":
        return lambda t: float(ramp_slope_fraction * beta_total * max(0.0, t - ramp_start))
    if transient == "sinusoidal":
        return lambda t: float(sinusoidal_amplitude_fraction * beta_total * np.sin(np.pi * t / sinusoidal_period))
    raise ValueError(f"Unsupported transient mode: {transient}")


def _validate_points() -> None:
    z_max, x_max, y_max, groups = MESH_SHAPE
    for label, (z_index, x_index, y_index) in POINTS_OF_INTEREST.items():
        if not (0 <= z_index < z_max and 0 <= x_index < x_max and 0 <= y_index < y_max):
            raise ValueError(f"{label} is out of bounds for mesh shape {MESH_SHAPE}.")
    if groups != 2:
        raise ValueError(f"Expected two energy groups, found {groups}.")


def _compute_nominal_shape_factors() -> dict[str, np.ndarray]:
    bundle = load_default_bundle()
    nominal_parameters = np.array([50.0, 50.0, 1.0, 1.0], dtype=float)
    _, flux_vector = predict_reactivity_and_flux(nominal_parameters, bundle=bundle)
    flux_vector = np.asarray(flux_vector, dtype=float)
    field = reshape_flux_vector(flux_vector)

    shape_factors: dict[str, np.ndarray] = {}
    for point_name, (z_index, x_index, y_index) in POINTS_OF_INTEREST.items():
        thermal_field = field[:, :, :, THERMAL_GROUP]
        fast_field = field[:, :, :, FAST_GROUP]

        thermal_norm = float(np.sum(np.abs(thermal_field))) or 1.0
        fast_norm = float(np.sum(np.abs(fast_field))) or 1.0

        shape_factors[point_name] = np.array(
            [
                float(field[z_index, x_index, y_index, THERMAL_GROUP] / thermal_norm),
                float(field[z_index, x_index, y_index, FAST_GROUP] / fast_norm),
            ],
            dtype=float,
        )

    return shape_factors


def simulate_transient(
    transient: str,
    t_final: float,
    dt: float,
    step_onset: float,
    step_fraction: float,
    ramp_start: float,
    ramp_slope_fraction: float,
    sinusoidal_amplitude_fraction: float,
    sinusoidal_period: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if transient not in TRANSIENT_MODES:
        raise ValueError(f"transient must be one of {TRANSIENT_MODES}.")

    beta_total = float(np.sum(thermal_default_params["beta"]))

    reactivity = build_reactivity_function(
        transient,
        beta_total,
        step_onset,
        step_fraction,
        ramp_start,
        ramp_slope_fraction,
        sinusoidal_amplitude_fraction,
        sinusoidal_period,
    )

    local_solver = PointKineticsEquationSolver(reactivity)
    time_points = np.linspace(0.0, t_final, int(max(2, np.ceil(t_final / dt))) + 1)
    local_solver.solve(t_span=(0.0, t_final), t_eval=time_points)
    solution = local_solver.solution
    assert solution is not None
    reactivity_history = np.asarray([reactivity(t) for t in time_points], dtype=float)
    return np.asarray(solution.t, dtype=float), np.asarray(solution.y[0], dtype=float), reactivity_history


def build_local_flux_histories(time_points: np.ndarray, neutron_density: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    shape_factors = _compute_nominal_shape_factors()
    point_names = list(POINTS_OF_INTEREST.keys())

    thermal_histories = np.zeros((time_points.size, len(point_names)), dtype=float)
    fast_histories = np.zeros_like(thermal_histories)

    for point_idx, point_name in enumerate(point_names):
        thermal_shape, fast_shape = shape_factors[point_name]
        thermal_histories[:, point_idx] = neutron_density * thermal_shape
        fast_histories[:, point_idx] = neutron_density * fast_shape

    return thermal_histories, fast_histories


def plot_local_fluxes(
    time_points: np.ndarray,
    thermal_histories: np.ndarray,
    fast_histories: np.ndarray,
    reactivity_history: np.ndarray,
    transient: str,
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)

    thermal_reference = max(float(abs(thermal_histories[0, 0])), 1e-30)
    fast_reference = max(float(abs(fast_histories[0, 0])), 1e-30)

    for point_idx, point_name in enumerate(POINTS_OF_INTEREST.keys()):
        axes[0].plot(time_points, thermal_histories[:, point_idx] / thermal_reference, linewidth=2.0, label=point_name)
        axes[1].plot(time_points, fast_histories[:, point_idx] / fast_reference, linewidth=2.0, label=point_name)

    thermal_rho_axis = axes[0].twinx()
    fast_rho_axis = axes[1].twinx()
    thermal_rho_axis.plot(time_points, reactivity_history, color="black", linestyle="--", linewidth=1.6, label="Reactivity")
    fast_rho_axis.plot(time_points, reactivity_history, color="black", linestyle="--", linewidth=1.6, label="Reactivity")

    axes[0].set_title(f"Thermal Local Flux Evolution | {transient.capitalize()} transient")
    axes[0].set_ylabel("Normalized flux")
    axes[0].set_yscale("log")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="best")
    thermal_rho_axis.set_ylabel(r"Reactivity $\rho$ [\$]")
    thermal_rho_axis.tick_params(axis="y", labelcolor="black")

    axes[1].set_title(f"Fast Local Flux Evolution | {transient.capitalize()} transient")
    axes[1].set_xlabel("Time [s]")
    axes[1].set_ylabel("Normalized flux")
    axes[1].set_yscale("log")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="best")
    fast_rho_axis.set_ylabel(r"Reactivity $\rho$ [\$]")
    fast_rho_axis.tick_params(axis="y", labelcolor="black")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple coupled point kinetics at three fixed local flux points.")
    parser.add_argument("--transient", choices=TRANSIENT_MODES, default="ramp")
    parser.add_argument("--t-final", type=float, default=10.0)
    parser.add_argument("--dt", type=float, default=0.001)
    parser.add_argument("--step-onset", type=float, default=2.0)
    parser.add_argument("--step-fraction", type=float, default=0.01)
    parser.add_argument("--ramp-start", type=float, default=2.0)
    parser.add_argument("--ramp-slope-fraction", type=float, default=0.05)
    parser.add_argument("--sin-amplitude-fraction", type=float, default=0.03)
    parser.add_argument("--sin-period", type=float, default=25.0)
    parser.add_argument("--out", type=Path, default=HERE / "simple_coupled_space_kinetics.png")
    return parser.parse_args()


def main() -> None:
    _validate_points()
    args = parse_args()

    time_points, neutron_density, reactivity_history = simulate_transient(
        transient=args.transient,
        t_final=args.t_final,
        dt=args.dt,
        step_onset=args.step_onset,
        step_fraction=args.step_fraction,
        ramp_start=args.ramp_start,
        ramp_slope_fraction=args.ramp_slope_fraction,
        sinusoidal_amplitude_fraction=args.sin_amplitude_fraction,
        sinusoidal_period=args.sin_period,
    )

    thermal_histories, fast_histories = build_local_flux_histories(time_points, neutron_density)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plot_local_fluxes(time_points, thermal_histories, fast_histories, reactivity_history, args.transient, args.out)
    print(f"Saved plot to {args.out}")


if __name__ == "__main__":
    main()