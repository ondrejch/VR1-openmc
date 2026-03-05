"""Unit tests for point-kinetics solver behavior and validation."""

from __future__ import annotations

import numpy as np
import pytest

from pke.solver import PointKineticsEquationSolver


def test_zero_reactivity_stays_at_steady_state() -> None:
    """With zero reactivity/source, normalized neutron density should remain 1."""
    solver = PointKineticsEquationSolver(lambda t: 0.0)
    t, n, _ = solver.solve(t_span=(0.0, 5.0), t_eval=np.linspace(0.0, 5.0, 200))
    assert len(t) == len(n)
    assert np.allclose(n, 1.0, atol=1e-8)


def test_invalid_kinetics_parameters_raise() -> None:
    """Parameter validator should reject invalid lambda/beta/Lambda definitions."""
    with pytest.raises(ValueError):
        PointKineticsEquationSolver(
            lambda t: 0.0,
            params={"beta": np.array([0.001]), "lambda_": np.array([-0.1]), "Lambda": 1e-4},
        )

    with pytest.raises(ValueError):
        PointKineticsEquationSolver(
            lambda t: 0.0,
            params={"beta": np.array([0.001]), "lambda_": np.array([0.1]), "Lambda": -1e-4},
        )
