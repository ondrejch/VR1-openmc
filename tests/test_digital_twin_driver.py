"""Tests for the coupled ROM + PRKE digital twin driver."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pandas")
pytest.importorskip("sklearn")

from digital_twin_files.coupled_rom_w_kinetics.digital_twin_driver import run_coupled_digital_twin
from digital_twin_files.rom.digital_twin import DigitalTwinBundle


class _LinearKeff:
    """Stand-in k-eff model: k = k0 + slope * cr1_height."""

    def __init__(self, k0: float, slope: float) -> None:
        self.k0, self.slope = k0, slope

    def predict(self, states: np.ndarray) -> np.ndarray:
        return self.k0 + self.slope * states[:, 0]


class _ConstantCoefficients:
    def predict(self, states: np.ndarray) -> np.ndarray:
        return np.ones((states.shape[0], 1))


def _bundle(k0: float, slope: float = 0.0) -> DigitalTwinBundle:
    return DigitalTwinBundle(
        data_root=Path("."),
        n_modes=1,
        keff_model=_LinearKeff(k0, slope),
        flux_model=_ConstantCoefficients(),
        pod_basis=np.ones((4, 1)),
        singular_values=np.ones(1),
    )


def test_constant_state_stays_critical_despite_rom_keff_bias() -> None:
    """A ROM k-eff offset at t=0 must not drive the steady-state PRKE."""
    schedule = np.tile([74.7, 84.7, 1.0, 1.0], (5, 1))
    result = run_coupled_digital_twin(schedule, dt_macro=0.5, dt_micro=0.01, bundle=_bundle(k0=1.005))
    assert np.allclose(result["neutron_density"], 1.0)
    assert np.allclose(result["reactivity_inserted"], 0.0)


def test_withdrawal_raises_power() -> None:
    """Reactivity added after t=0 still drives the kinetics."""
    schedule = np.column_stack([np.linspace(74.7, 84.7, 5), np.full(5, 84.7), np.ones(5), np.ones(5)])
    result = run_coupled_digital_twin(schedule, dt_macro=0.5, dt_micro=0.01, bundle=_bundle(k0=0.99, slope=1e-5))
    assert result["neutron_density"][-1] > 1.0
