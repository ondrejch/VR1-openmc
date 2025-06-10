from pke.solver import PointKineticsEquationSolver
import numpy as np
import matplotlib.pyplot as plt


# Define reactivity function (ramp insertion)
def ramp_rho(t: float) -> float:
    return 0.5 * solver.beta_total * max(0, t - 2)  # 0.5$/s ramp starting at t=2s


# Initialize and solve
solver = PointKineticsEquationSolver(ramp_rho)
solver.solve(t_span=(0, 5), t_eval=np.linspace(0, 5, 4000))

# Create separate plots
fig1, ax1 = solver.plot_neutron_density(logscale=True, linewidth=2, color='darkred')
fig2, ax2 = solver.plot_precursors(groups=[0, 1, 5],  # Plot first, second, and sixth groups
                                   linestyle='--', alpha=0.8)

plt.show()
