from pke.solver import PointKineticsEquationSolver
import numpy as np
import matplotlib.pyplot as plt


# Example 1: Constant source with step reactivity
def step_reactivity(t: float) -> float:
    return 1e-3 * solver.beta_total if (100 < t < 200) else 0


def constant_source(t):
    return 1e-2  # Constant external source


solver = PointKineticsEquationSolver(step_reactivity, constant_source)
solver.solve(t_span=(0, 400))
solver.plot_neutron_density(logscale=False, color='blue', linewidth=2)
solver.plot_source_contribution()


# Example 2: Pulsed neutron source (startup scenario)
def zero_reactivity(t):
    return 0.0  # No reactivity insertion


def pulsed_source(t):
    if 0 <= t <= 5:
        return np.exp(-(t - 1.5) ** 2 / 0.01)  # Gaussian pulse
    if 50 <= t <= 55:
        return np.exp(-(t - 51.5) ** 2 / 0.01)  # Gaussian pulse
    return 0.0


solver2 = PointKineticsEquationSolver(zero_reactivity, pulsed_source)
solver2.solve(t_span=(0, 100), t_eval=np.linspace(0, 100, 10000))
solver2.plot_neutron_density(logscale=False)
solver2.plot_source_contribution()
