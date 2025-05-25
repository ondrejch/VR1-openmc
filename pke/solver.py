import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

thermal_default_params: dict = {
    'beta': np.array([0.000215, 0.00142, 0.00127, 0.00257, 0.00075, 0.00027]),
    'lambda_': np.array([0.0126, 0.0337, 0.139, 0.325, 1.13, 2.50]),
    'Lambda': 5e-4
}

fast_reactor_params: dict = {
    'beta': np.array([0.00022, 0.00142, 0.00127, 0.00257, 0.00075, 0.00027]),
    'lambda_': np.array([0.0126, 0.0337, 0.139, 0.325, 1.13, 2.50]),
    'Lambda': 1e-7
}


class PointKineticsEquationSolver:
    def __init__(self, reactivity_func, source_func=None, params=None):
        """ Nuclear reactor point kinetics analyzer with modular plotting
        Args:
            reactivity_func (callable): ρ(t) in dollars
            params (dict): Reactor parameters (default: U-235 thermal) """
        if params is None:
            params = thermal_default_params
        self.params = params
        self.beta = params['beta']
        self.lambda_ = params['lambda_']
        self.Lambda = params['Lambda']
        self.beta_total = np.sum(self.beta)
        self._validate_parameters()
        self.reactivity_func = reactivity_func
        if source_func is None:
            source_func = (lambda t: 0.0)  # Default: no source
        self.source_func = source_func
        self.solution = None

    def _validate_parameters(self):
        if len(self.params['beta']) != len(self.params['lambda_']) or len(self.params['beta']) < 1:
            raise ValueError("Beta and lambda arrays must have equal length")

    def solve(self, t_span=(0, 10), t_eval=None):
        """Solve the point kinetics equations"""
        beta = self.params['beta']
        lambda_ = self.params['lambda_']
        Lambda = self.params['Lambda']

        # Initial conditions (steady-state)
        n0 = 1.0
        C0 = beta / (lambda_ * Lambda) * n0
        y0 = np.concatenate(([n0], C0))

        def equations(t, y):
            n, *C = y
            rho = self.reactivity_func(t)       # External reactivity
            Q = self.source_func(t)             # External neutron source
            prompt = (rho - beta.sum()) / Lambda
            delayed = np.dot(lambda_, C)

            dndt = n * prompt + delayed + Q
            dCdt = (beta[i] / Lambda * n - lambda_[i] * C[i] for i in range(len(C)))

            return [dndt, *dCdt]

        self.solution = solve_ivp(equations, t_span, y0, method='RK45', t_eval=t_eval, rtol=1e-6, atol=1e-8)

        return self.solution.t, self.solution.y[0], self.solution.y[1:]

    def plot_neutron_density(self, figsize=(8, 4), logscale=True, **plot_kwargs):
        """ Plot neutron density temporal evolution
        Args:
            logscale (bool): Use logarithmic y-axis
            **plot_kwargs: Matplotlib styling options """
        if not self.solution:
            raise RuntimeError("Call solve() before plotting")
        fig, ax = plt.subplots(figsize=figsize)
        if logscale:
            ax.semilogy(self.solution.t, self.solution.y[0], **plot_kwargs)
        else:
            ax.plot(self.solution.t, self.solution.y[0], **plot_kwargs)

        ax.set(xlabel='Time (s)', ylabel='Relative Neutron Density', title='Point Kinetics Neutron Density')
        ax.grid(True, which='both' if logscale else 'major', alpha=0.4)
        return fig, ax

    def plot_precursors(self, groups='all', figsize=(10, 6), **plot_kwargs):
        """ Plot precursor group concentrations
        Args:
            groups: List of group indices (0-based) or 'all' """
        if not self.solution:
            raise RuntimeError("Call solve() before plotting")

        fig, ax = plt.subplots(figsize=figsize)
        C = self.solution.y[1:]
        groups = range(len(C)) if groups == 'all' else groups
        for i in groups:
            ax.plot(self.solution.t, C[i], label=f'Group {i + 1}', **plot_kwargs)
        ax.set(xlabel='Time [s]', ylabel='Precursor Concentration', title='Delayed Neutron Precursors')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.4)
        return fig, ax

    def plot_source_contribution(self, figsize=(8, 4)):
        """Plot the external source function over time"""
        if not self.solution:
            raise RuntimeError("Call solve() before plotting")

        fig, ax = plt.subplots(figsize=figsize)
        source_values = [self.source_func(t) for t in self.solution.t]

        ax.plot(self.solution.t, source_values, 'r--', linewidth=2)
        ax.set(
            xlabel='Time (s)',
            ylabel='Source Strength [neutrons/s]',
            title='External Neutron Source Function'
        )
        ax.grid(True, alpha=0.4)
        plt.show()
        return fig, ax

    def plot(self, figsize=(12, 6), logscale=False, **plot_kwargs):
        """ Generate diagnostic plots for neutron density and precursor concentrations """
        if self.solution is None:
            raise RuntimeError("No solution available. Call solve() first.")
        t = self.solution.t
        n = self.solution.y[0]
        C = self.solution.y[1:]

        plt.figure(figsize=figsize)
        # Neutron density plot (log scale)
        plt.subplot(1, 2, 1)
        if logscale:
            plt.semilogy(t, n, 'b-', linewidth=2)
        else:
            plt.plot(t, n, 'b-', linewidth=2)
        plt.xlabel('Time [s]', fontsize=12)
        plt.ylabel('Relative Neutron Density', fontsize=12)
        plt.title('Neutron Population', fontsize=14)
        plt.grid(True, which='both', linestyle='--', alpha=0.7)

        # Precursor concentrations plot
        plt.subplot(1, 2, 2)
        for i, Ci in enumerate(C):
            plt.plot(t, Ci, label=f'Group {i + 1}')
        plt.xlabel('Time [s]', fontsize=12)
        plt.ylabel('Precursor Concentration', fontsize=12)
        plt.title('Precursors', fontsize=14)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        # plt.show()
        return plt
