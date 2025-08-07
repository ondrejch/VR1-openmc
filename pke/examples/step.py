from pke.solver import PointKineticsEquationSolver
import matplotlib.pyplot as plt
# import matplotlib
# import PyQt5
# matplotlib.use('TkAgg')  # 'TkAgg' or 'Qt5Agg' if you have PyQt5 installed, necessary for matplotlib>=3.10


def step_reactivity1(t: float) -> float:
    return 0.1 * solver.beta_total if t >= 100 else 0


def step_reactivity(t: float) -> float:
    return 1e-4 if (100 < t < 200) else 0


# Initialize and solve
solver = PointKineticsEquationSolver(step_reactivity)
t, n, C = solver.solve(t_span=(0, 400))
# print((t, n, C))

# Generate plots
plt = solver.plot()
plt.show()
plt.savefig('my_reactivity.png')
