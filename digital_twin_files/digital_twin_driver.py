"""Coupled VR-1 digital twin driver using an adiabatic approximation.

This wrapper couples:
1) The static ROM in ``vr1.digital_twin`` for shape/reactivity updates.
2) The PRKE model in ``pke.solver`` for kinetics on a finer time grid.

At each macro step, the ROM updates reactivity and flux shape.
Inside each macro interval, the PRKE state is advanced with micro steps using
linearly interpolated reactivity between consecutive ROM macro points.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np

from digital_twin import DigitalTwinBundle
from digital_twin import reshape_flux_vector
from digital_twin import predict_reactivity_and_flux

try:
    from pke.solver import thermal_default_params
except Exception:
    # Fallback keeps this driver runnable even if optional SciPy dependency
    # used by pke.solver's ODE utilities is unavailable in the environment.
    thermal_default_params = {
        "beta": np.array([0.000215, 0.00142, 0.00127, 0.00257, 0.00075, 0.00027]),
        "lambda_": np.array([0.0126, 0.0337, 0.139, 0.325, 1.13, 2.50]),
        "Lambda": 5e-4,
    }


@dataclass
class PRKEState:
    """State container for PRKE integration."""

    neutron_density: float
    precursors: np.ndarray


class PRKEMicroStepper:
    """Stateful micro-step integrator for point kinetics equations."""

    def __init__(self, params: dict[str, np.ndarray | float] | None = None, p0: float = 1.0):
        if params is None:
            params = thermal_default_params

        self.beta = np.asarray(params["beta"], dtype=float)
        self.lambda_ = np.asarray(params["lambda_"], dtype=float)
        self.Lambda = float(params["Lambda"])
        self.beta_total = float(np.sum(self.beta))

        # Steady-state precursor initialization for the given initial neutron density.
        c0 = self.beta / (self.lambda_ * self.Lambda) * float(p0)
        self.state = PRKEState(neutron_density=float(p0), precursors=c0)

    def _rhs(self, neutron_density: float, precursors: np.ndarray, rho: float) -> tuple[float, np.ndarray]:
        prompt_term = ((rho - self.beta_total) / self.Lambda) * neutron_density
        delayed_term = float(np.dot(self.lambda_, precursors))
        dndt = prompt_term + delayed_term
        dcdt = self.beta / self.Lambda * neutron_density - self.lambda_ * precursors
        return dndt, dcdt

    def step_rk4(self, dt: float, rho_func: Callable[[float], float], local_time: float) -> None:
        """Advance one micro step with RK4 using a time-varying reactivity."""

        n0 = self.state.neutron_density
        c0 = self.state.precursors

        rho1 = float(rho_func(local_time))
        k1_n, k1_c = self._rhs(n0, c0, rho1)

        rho2 = float(rho_func(local_time + 0.5 * dt))
        k2_n, k2_c = self._rhs(n0 + 0.5 * dt * k1_n, c0 + 0.5 * dt * k1_c, rho2)
        k3_n, k3_c = self._rhs(n0 + 0.5 * dt * k2_n, c0 + 0.5 * dt * k2_c, rho2)

        rho4 = float(rho_func(local_time + dt))
        k4_n, k4_c = self._rhs(n0 + dt * k3_n, c0 + dt * k3_c, rho4)

        n_next = n0 + (dt / 6.0) * (k1_n + 2.0 * k2_n + 2.0 * k3_n + k4_n)
        c_next = c0 + (dt / 6.0) * (k1_c + 2.0 * k2_c + 2.0 * k3_c + k4_c)

        self.state = PRKEState(neutron_density=float(n_next), precursors=c_next)


def _validate_parameter_schedule(parameter_schedule: np.ndarray) -> None:
    if parameter_schedule.ndim != 2 or parameter_schedule.shape[1] != 4:
        raise ValueError("parameter_schedule must have shape (n_macro_points, 4).")
    if parameter_schedule.shape[0] < 2:
        raise ValueError("parameter_schedule must include at least two macro points.")


def _linear_reactivity_profile(rho_start: float, rho_end: float, dt_macro: float) -> Callable[[float], float]:
    def rho_of_tau(tau: float) -> float:
        alpha = np.clip(tau / dt_macro, 0.0, 1.0)
        return float(rho_start + alpha * (rho_end - rho_start))

    return rho_of_tau


def run_coupled_digital_twin(
    parameter_schedule: np.ndarray,
    dt_macro: float = 0.5,
    dt_micro: float = 0.001,
    bundle: DigitalTwinBundle | None = None,
    kinetics_params: dict[str, np.ndarray | float] | None = None,
) -> dict[str, np.ndarray]:
    """Run adiabatically coupled ROM + PRKE simulation on dual time grids.

    Args:
        parameter_schedule: Array of shape (n_macro_points, 4). Each row is
            [cr1_height, cr2_height, dummy_water_density, fa_water_density]
            at one macro grid point.
        dt_macro: Macro-step size in seconds for ROM updates.
        dt_micro: Micro-step size in seconds for PRKE updates.
        bundle: Optional pre-trained digital twin bundle.
        kinetics_params: Optional PRKE parameters dictionary.

    Returns:
        A dictionary with arrays:
        - time: Macro-grid time points.
        - reactivity_macro: ROM reactivity at macro points.
        - neutron_density: P(t) at macro points.
        - flux_vectors: ROM flux vectors at macro points.
        - localized_power: P(t) * flux_vector at macro points.
    """

    if dt_macro <= 0.0 or dt_micro <= 0.0:
        raise ValueError("dt_macro and dt_micro must be positive.")
    if dt_micro > dt_macro:
        raise ValueError("dt_micro must be <= dt_macro.")

    parameter_schedule = np.asarray(parameter_schedule, dtype=float)
    _validate_parameter_schedule(parameter_schedule)

    reactivity_macro, flux_vectors = predict_reactivity_and_flux(parameter_schedule, bundle=bundle)
    reactivity_macro = np.asarray(reactivity_macro, dtype=float)
    flux_vectors = np.asarray(flux_vectors, dtype=float)

    n_macro_points = parameter_schedule.shape[0]
    macro_times = np.arange(n_macro_points, dtype=float) * dt_macro

    stepper = PRKEMicroStepper(params=kinetics_params, p0=1.0)
    neutron_density_macro = np.zeros(n_macro_points, dtype=float)
    localized_power_macro = np.zeros_like(flux_vectors)

    # Initial condition at t=0.
    neutron_density_macro[0] = stepper.state.neutron_density
    localized_power_macro[0] = neutron_density_macro[0] * flux_vectors[0]

    for macro_idx in range(n_macro_points - 1):
        rho_start = float(reactivity_macro[macro_idx])
        rho_end = float(reactivity_macro[macro_idx + 1])
        rho_of_tau = _linear_reactivity_profile(rho_start, rho_end, dt_macro)

        tau = 0.0
        while tau < dt_macro:
            dt_step = min(dt_micro, dt_macro - tau)
            stepper.step_rk4(dt_step, rho_of_tau, tau)
            tau += dt_step

        neutron_density_macro[macro_idx + 1] = stepper.state.neutron_density
        localized_power_macro[macro_idx + 1] = stepper.state.neutron_density * flux_vectors[macro_idx + 1]

    return {
        "time": macro_times,
        "reactivity_macro": reactivity_macro,
        "neutron_density": neutron_density_macro,
        "flux_vectors": flux_vectors,
        "localized_power": localized_power_macro,
    }


def _build_linear_parameter_schedule(
    n_macro_points: int,
    cr1_start: float,
    cr1_end: float,
    cr2_start: float,
    cr2_end: float,
    dummy_water: float,
    fa_water: float,
) -> np.ndarray:
    cr1 = np.linspace(cr1_start, cr1_end, n_macro_points)
    cr2 = np.linspace(cr2_start, cr2_end, n_macro_points)
    dummy = np.full(n_macro_points, dummy_water, dtype=float)
    fa = np.full(n_macro_points, fa_water, dtype=float)
    return np.column_stack([cr1, cr2, dummy, fa])


def save_summary_plot(
    result: dict[str, np.ndarray],
    parameter_schedule: np.ndarray,
    output_path: str = "coupled_digital_twin_summary.png",
    z_index: int = 35,
) -> None:
    """Save a compact visualization of coupled twin outputs."""

    time = result["time"]
    reactivity = result["reactivity_macro"]
    neutron_density = result["neutron_density"]
    localized_power = result["localized_power"]

    total_power = np.sum(localized_power, axis=1)
    normalized_power = total_power / total_power[0]

    # Avoid zeros or negative numbers when plotting on log scale
    eps = 1e-12
    neutron_density_plot = np.maximum(neutron_density, eps)
    normalized_power_plot = np.maximum(normalized_power, eps)

    final_localized_flux = reshape_flux_vector(localized_power[-1])
    thermal_slice = final_localized_flux[z_index, :, :, 0]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    axes[0, 0].plot(time, reactivity, marker="o", color="tab:red")
    axes[0, 0].set_title("Macro Reactivity")
    axes[0, 0].set_xlabel("Time [s]")
    axes[0, 0].set_ylabel("rho [delta-k/k]")
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].semilogy(time, neutron_density_plot, marker="o", color="tab:blue")
    axes[0, 1].set_title("PRKE Relative Neutron Density (log scale)")
    axes[0, 1].set_xlabel("Time [s]")
    axes[0, 1].set_ylabel("P(t)")
    axes[0, 1].grid(True, which='both', alpha=0.3)

    axes[1, 0].semilogy(time, normalized_power_plot, marker="o", color="tab:green")
    axes[1, 0].set_title("Normalized Total Core Power (log scale)")
    axes[1, 0].set_xlabel("Time [s]")
    axes[1, 0].set_ylabel("P_total / P_total(t=0)")
    axes[1, 0].grid(True, which='both', alpha=0.3)

    im = axes[1, 1].imshow(thermal_slice, origin="lower", cmap="inferno")
    axes[1, 1].set_title(f"Final Localized Thermal Power (z={z_index})")
    axes[1, 1].set_xlabel("X index")
    axes[1, 1].set_ylabel("Y index")
    fig.colorbar(im, ax=axes[1, 1], label="Arbitrary units")

    cr1_start = float(parameter_schedule[0, 0])
    cr1_end = float(parameter_schedule[-1, 0])
    fig.suptitle(f"Coupled Digital Twin Summary | CR1 {cr1_start:.1f} -> {cr1_end:.1f} cm")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run coupled VR-1 ROM + PRKE adiabatic driver.")
    parser.add_argument("--t-final", type=float, default=2.0, help="Final simulation time in seconds.")
    parser.add_argument("--dt-macro", type=float, default=0.5, help="Macro-step size [s] for ROM updates.")
    parser.add_argument("--dt-micro", type=float, default=0.001, help="Micro-step size [s] for PRKE updates.")
    parser.add_argument("--cr1-start", type=float, default=74.7, help="Initial CR1 height [cm].")
    parser.add_argument("--cr1-end", type=float, default=84.7, help="Final CR1 height [cm].")
    parser.add_argument("--cr2-start", type=float, default=84.7, help="Initial CR2 height [cm].")
    parser.add_argument("--cr2-end", type=float, default=84.7, help="Final CR2 height [cm].")
    parser.add_argument("--dummy-water", type=float, default=1.0, help="Dummy channel water density multiplier.")
    parser.add_argument("--fa-water", type=float, default=1.0, help="Fuel assembly water density multiplier.")
    parser.add_argument("--output", type=str, default="coupled_digital_twin_results.npz", help="Output NPZ path.")
    parser.add_argument("--plot-output", type=str, default="coupled_digital_twin_summary.png", help="Output summary figure path.")
    parser.add_argument("--z-index", type=int, default=35, help="Z index for final thermal power map plot.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    n_macro_points = int(np.floor(args.t_final / args.dt_macro)) + 1

    parameter_schedule = _build_linear_parameter_schedule(
        n_macro_points=n_macro_points,
        cr1_start=args.cr1_start,
        cr1_end=args.cr1_end,
        cr2_start=args.cr2_start,
        cr2_end=args.cr2_end,
        dummy_water=args.dummy_water,
        fa_water=args.fa_water,
    )

    result = run_coupled_digital_twin(
        parameter_schedule=parameter_schedule,
        dt_macro=args.dt_macro,
        dt_micro=args.dt_micro,
    )

    np.savez_compressed(args.output, **result, parameter_schedule=parameter_schedule)
    save_summary_plot(result, parameter_schedule, output_path=args.plot_output, z_index=args.z_index)
    print(f"Saved coupled digital twin results to {args.output}")
    print(f"Saved summary plot to {args.plot_output}")
    print(f"Final neutron density P(t_final): {result['neutron_density'][-1]:.6f}")


if __name__ == "__main__":
    main()