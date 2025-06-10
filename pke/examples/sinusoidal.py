from pke.solver import PointKineticsEquationSolver
import numpy as np
import matplotlib.pyplot as plt


# Custom reactivity function (sinusoidal)
def sinusoidal_rho(t: float) -> float:
    return 0.3 * solver.beta_total * np.sin(np.pi * t / 25.0)


# Initialize and solve
t_max: float = 500.0
solver = PointKineticsEquationSolver(sinusoidal_rho)
solver.solve(t_span=(0, t_max), t_eval=np.linspace(0, t_max, int(t_max*1e4)))

# Create separate plots
fig1, ax1 = solver.plot_neutron_density(logscale=False, linewidth=2, color='darkred')
fig2, ax2 = solver.plot_precursors(groups=list(range(6)), linestyle='--', alpha=0.9)

plt.show()
