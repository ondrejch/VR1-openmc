#!/usr/bin/env python3
"""Visualize localized point-kinetics evolution during a small rod insertion transient.

This script couples the static ROM in ``digital_twin_files.rom.digital_twin``
with the PRKE micro-stepper from ``digital_twin_driver.py``. At each macro step
the ROM is queried for reactivity and flux shape, the flux vector is reshaped to
the VR-1 mesh, and the localized thermal/fast flux is tracked at three points.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from digital_twin_files.coupled_rom_w_kinetics.digital_twin_driver import PRKEMicroStepper
from digital_twin_files.coupled_rom_w_kinetics.digital_twin_driver import thermal_default_params
from digital_twin_files.rom.digital_twin import DigitalTwinBundle
from digital_twin_files.rom.digital_twin import MESH_SHAPE
from digital_twin_files.rom.digital_twin import load_default_bundle
from digital_twin_files.rom.digital_twin import predict_reactivity_and_flux
from digital_twin_files.rom.digital_twin import reshape_flux_vector


POINTS_OF_INTEREST: dict[str, tuple[int, int, int]] = {
    "Fuel": (35, 60, 60),
    "Control Rod": (35, 65, 82),
    "Moderator": (35, 65, 38),
}

THERMAL_GROUP = 0
FAST_GROUP = 1
ROD_HEIGHT_LIMITS = (0.0, 84.7)
TRANSIENT_MODES = ("step", "ramp", "sinusoidal")


def _example_reactivity_profile(
    transient: str,
    beta_total: float,
    step_onset: float,
    step_fraction: float,
    ramp_start: float,
    ramp_slope_fraction: float,
    sinusoidal_amplitude_fraction: float,
    sinusoidal_period: float,
) -> Callable[[float], float]:
    if transient == "step":
        return lambda t: float(step_fraction * beta_total if t >= step_onset else 0.0)
    if transient == "ramp":
        return lambda t: float(ramp_slope_fraction * beta_total * max(0.0, t - ramp_start))
    if transient == "sinusoidal":
        return lambda t: float(sinusoidal_amplitude_fraction * beta_total * np.sin(np.pi * t / sinusoidal_period))
    raise ValueError(f"Unsupported transient mode: {transient}")


def _example_insertion_fraction(
    transient: str,
    time_value: float,
    step_onset: float,
    ramp_start: float,
    ramp_duration: float,
    sinusoidal_period: float,
) -> float:
    if transient == "step":
        return 1.0 if time_value >= step_onset else 0.0
    if transient == "ramp":
        if ramp_duration <= 0.0:
            return 1.0 if time_value >= ramp_start else 0.0
        return float(np.clip((time_value - ramp_start) / ramp_duration, 0.0, 1.0))
    if transient == "sinusoidal":
        return float(0.5 * (1.0 + np.sin(np.pi * time_value / sinusoidal_period)))
    raise ValueError(f"Unsupported transient mode: {transient}")


def _rod_height_profile(
    transient: str,
    time_value: float,
    rod_start_height: float,
    rod_insertion_cm: float,
    step_onset: float,
    ramp_start: float,
    ramp_duration: float,
    sinusoidal_period: float,
) -> float:
    insertion_fraction = _example_insertion_fraction(
        transient,
        time_value,
        step_onset,
        ramp_start,
        ramp_duration,
        sinusoidal_period,
    )
    height = rod_start_height - rod_insertion_cm * insertion_fraction
    return float(np.clip(height, *ROD_HEIGHT_LIMITS))


def _selected_control_rod_height(control_rod: str, moving_height: float, fixed_height: float) -> tuple[float, float]:
    control_rod = control_rod.upper()
    if control_rod == "CR1":
        return moving_height, fixed_height
    if control_rod == "CR2":
        return fixed_height, moving_height
    raise ValueError("control_rod must be either 'CR1' or 'CR2'.")


def _rod_height_at_time(
    time_value: float,
    rod_start_height: float,
    rod_insertion_cm: float,
    insertion_duration: float,
) -> float:
    if insertion_duration <= 0.0:
        return float(rod_start_height - rod_insertion_cm)

    if time_value <= insertion_duration:
        fraction = time_value / insertion_duration
        height = rod_start_height - rod_insertion_cm * fraction
    else:
        height = rod_start_height - rod_insertion_cm

    return float(np.clip(height, *ROD_HEIGHT_LIMITS))


def _build_parameter_vector(
    time_value: float,
    rod_start_height: float,
    rod_insertion_cm: float,
    insertion_duration: float,
    fixed_cr2_height: float,
    dummy_water_density_multiplier: float,
    fuel_assembly_water_density_multiplier: float,
) -> np.ndarray:
    cr1_height = _rod_height_at_time(time_value, rod_start_height, rod_insertion_cm, insertion_duration)
    cr2_height = float(np.clip(fixed_cr2_height, *ROD_HEIGHT_LIMITS))
    return np.array(
        [
            cr1_height,
            cr2_height,
            float(dummy_water_density_multiplier),
            float(fuel_assembly_water_density_multiplier),
        ],
        dtype=float,
    )


def _shape_factor_at_point(field: np.ndarray, point: tuple[int, int, int], group: int) -> float:
    z_index, x_index, y_index = point
    group_field = np.asarray(field[:, :, :, group], dtype=float)
    normalization = float(np.sum(np.abs(group_field)))
    if normalization <= 0.0:
        normalization = 1.0
    return float(field[z_index, y_index, x_index, group] / normalization)


def _validate_points(points: dict[str, tuple[int, int, int]]) -> None:
    z_max, x_max, y_max, group_count = MESH_SHAPE
    for label, (z_index, x_index, y_index) in points.items():
        if not (0 <= z_index < z_max):
            raise ValueError(f"{label} z-index {z_index} is out of bounds for mesh depth {z_max}.")
        if not (0 <= x_index < x_max):
            raise ValueError(f"{label} x-index {x_index} is out of bounds for mesh width {x_max}.")
        if not (0 <= y_index < y_max):
            raise ValueError(f"{label} y-index {y_index} is out of bounds for mesh width {y_max}.")
        if group_count != 2:
            raise ValueError(f"Expected a two-group mesh, got {group_count} groups.")


def _precompute_macro_profiles(
    macro_times: np.ndarray,
    points: dict[str, tuple[int, int, int]],
    transient: str,
    control_rod: str,
    rod_start_height: float,
    rod_insertion_cm: float,
    insertion_duration: float,
    fixed_cr2_height: float,
    dummy_water_density_multiplier: float,
    fuel_assembly_water_density_multiplier: float,
    step_onset: float,
    step_fraction: float,
    ramp_start: float,
    ramp_slope_fraction: float,
    ramp_duration: float,
    sinusoidal_amplitude_fraction: float,
    sinusoidal_period: float,
    bundle: DigitalTwinBundle | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if bundle is None:
        bundle = load_default_bundle()

    beta_total = float(np.sum(thermal_default_params["beta"]))
    rho_profile = _example_reactivity_profile(
        transient,
        beta_total,
        step_onset,
        step_fraction,
        ramp_start,
        ramp_slope_fraction,
        sinusoidal_amplitude_fraction,
        sinusoidal_period,
    )

    n_macro = macro_times.size
    n_points = len(points)
    reactivity_macro = np.zeros(n_macro, dtype=float)
    rod_height_macro = np.zeros(n_macro, dtype=float)
    psi_macro = np.zeros((n_macro, n_points, 2), dtype=float)

    point_items = list(points.items())
    for macro_idx, time_value in enumerate(macro_times):
        moving_height = _rod_height_profile(
            transient,
            time_value,
            rod_start_height,
            rod_insertion_cm,
            step_onset,
            ramp_start,
            ramp_duration,
            sinusoidal_period,
        )
        rod_height_macro[macro_idx] = moving_height

        cr1_height, cr2_height = _selected_control_rod_height(control_rod, moving_height, fixed_cr2_height)
        parameter_vector = np.array(
            [
                cr1_height,
                cr2_height,
                float(dummy_water_density_multiplier),
                float(fuel_assembly_water_density_multiplier),
            ],
            dtype=float,
        )
        _, flux_vector = predict_reactivity_and_flux(parameter_vector, bundle=bundle)
        flux_vector = np.asarray(flux_vector, dtype=float)
        field = reshape_flux_vector(flux_vector)
        if field.shape != MESH_SHAPE:
            raise ValueError(f"Reshaped flux field has shape {field.shape}, expected {MESH_SHAPE}.")

        reactivity_macro[macro_idx] = float(rho_profile(time_value))
        for point_idx, (_, point) in enumerate(point_items):
            psi_macro[macro_idx, point_idx, THERMAL_GROUP] = _shape_factor_at_point(field, point, THERMAL_GROUP)
            psi_macro[macro_idx, point_idx, FAST_GROUP] = _shape_factor_at_point(field, point, FAST_GROUP)

    return reactivity_macro, rod_height_macro, psi_macro, macro_times


def simulate_point_kinetics(
    total_time: float,
    dt_macro: float,
    dt_micro: float,
    transient: str,
    control_rod: str,
    rod_start_height: float,
    rod_insertion_cm: float,
    insertion_duration: float,
    fixed_cr2_height: float,
    dummy_water_density_multiplier: float,
    fuel_assembly_water_density_multiplier: float,
    step_onset: float,
    step_fraction: float,
    ramp_start: float,
    ramp_slope_fraction: float,
    ramp_duration: float,
    sinusoidal_amplitude_fraction: float,
    sinusoidal_period: float,
    p0: float = 1.0,
    kinetics_params: dict[str, np.ndarray | float] | None = None,
    bundle: DigitalTwinBundle | None = None,
) -> dict[str, np.ndarray | str]:
    if total_time <= 0.0:
        raise ValueError("total_time must be positive.")
    if dt_macro <= 0.0 or dt_micro <= 0.0:
        raise ValueError("dt_macro and dt_micro must be positive.")
    if dt_micro > dt_macro:
        raise ValueError("dt_micro must be <= dt_macro.")
    if transient not in TRANSIENT_MODES:
        raise ValueError(f"transient must be one of {TRANSIENT_MODES}.")

    if kinetics_params is None:
        kinetics_params = thermal_default_params

    macro_times = np.arange(0.0, total_time + 0.5 * dt_macro, dt_macro, dtype=float)
    if macro_times[-1] < total_time:
        macro_times = np.append(macro_times, total_time)
    else:
        macro_times[-1] = total_time

    reactivity_macro, rod_height_macro, psi_macro, macro_times = _precompute_macro_profiles(
        macro_times,
        POINTS_OF_INTEREST,
        transient,
        control_rod,
        rod_start_height,
        rod_insertion_cm,
        insertion_duration,
        fixed_cr2_height,
        dummy_water_density_multiplier,
        fuel_assembly_water_density_multiplier,
        step_onset,
        step_fraction,
        ramp_start,
        ramp_slope_fraction,
        ramp_duration,
        sinusoidal_amplitude_fraction,
        sinusoidal_period,
        bundle=bundle,
    )

    point_names = list(POINTS_OF_INTEREST.keys())
    n_points = len(point_names)

    beta_total = float(np.sum(kinetics_params["beta"]))
    rho_schedule = _example_reactivity_profile(
        transient,
        beta_total,
        step_onset,
        step_fraction,
        ramp_start,
        ramp_slope_fraction,
        sinusoidal_amplitude_fraction,
        sinusoidal_period,
    )

    stepper = PRKEMicroStepper(params=kinetics_params, p0=p0)
    time_history = [0.0]
    neutron_history = [float(stepper.state.neutron_density)]
    thermal_history = [[float(p0 * psi_macro[0, point_idx, THERMAL_GROUP])] for point_idx in range(n_points)]
    fast_history = [[float(p0 * psi_macro[0, point_idx, FAST_GROUP])] for point_idx in range(n_points)]

    for macro_idx in range(macro_times.size - 1):
        interval_start = float(macro_times[macro_idx])
        interval_duration = float(macro_times[macro_idx + 1] - macro_times[macro_idx])
        rho_of_tau = lambda tau, interval_start=interval_start: rho_schedule(interval_start + tau)

        tau = 0.0
        while tau < interval_duration - 1e-15:
            dt_step = min(dt_micro, interval_duration - tau)
            stepper.step_rk4(dt_step, rho_of_tau, tau)
            tau += dt_step

            if tau < interval_duration - 1e-15:
                current_time = interval_start + tau
                neutron_density = float(stepper.state.neutron_density)
                time_history.append(current_time)
                neutron_history.append(neutron_density)
                for point_idx in range(n_points):
                    thermal_history[point_idx].append(neutron_density * psi_macro[macro_idx, point_idx, THERMAL_GROUP])
                    fast_history[point_idx].append(neutron_density * psi_macro[macro_idx, point_idx, FAST_GROUP])

        boundary_time = interval_start + interval_duration
        neutron_density = float(stepper.state.neutron_density)
        time_history.append(boundary_time)
        neutron_history.append(neutron_density)

        boundary_macro_idx = macro_idx + 1
        for point_idx in range(n_points):
            thermal_history[point_idx].append(neutron_density * psi_macro[boundary_macro_idx, point_idx, THERMAL_GROUP])
            fast_history[point_idx].append(neutron_density * psi_macro[boundary_macro_idx, point_idx, FAST_GROUP])

    return {
        "time": np.asarray(time_history, dtype=float),
        "reactivity_macro": np.asarray(reactivity_macro, dtype=float),
        "control_rod_height": np.asarray(rod_height_macro, dtype=float),
        "neutron_density": np.asarray(neutron_history, dtype=float),
        "thermal_flux": np.asarray(thermal_history, dtype=float).T,
        "fast_flux": np.asarray(fast_history, dtype=float).T,
        "macro_times": np.asarray(macro_times, dtype=float),
        "transient": transient,
        "control_rod": control_rod.upper(),
    }


def plot_full_kinetics(
    macro_time: np.ndarray,
    micro_time: np.ndarray,
    reactivity_macro: np.ndarray,
    rod_height_macro: np.ndarray,
    thermal_series: np.ndarray,
    fast_series: np.ndarray,
    transient: str,
    control_rod: str,
    out_path: Path | None = None,
) -> tuple[Figure, np.ndarray]:
    fig, axes = plt.subplots(4, 1, figsize=(13, 13))

    onset_index = np.flatnonzero(np.abs(np.diff(reactivity_macro)) > 1e-12)
    onset_time = float(macro_time[onset_index[0] + 1]) if onset_index.size > 0 else float(macro_time[0])

    thermal_reference = np.maximum(np.abs(thermal_series[0]), 1e-30)
    fast_reference = np.maximum(np.abs(fast_series[0]), 1e-30)
    thermal_normalized = thermal_series / thermal_reference
    fast_normalized = fast_series / fast_reference

    group_specs = (
        (axes[2], thermal_normalized, "Thermal Flux"),
        (axes[3], fast_normalized, "Fast Flux"),
    )

    axes[0].plot(macro_time, reactivity_macro, color="tab:red", linewidth=2.0)
    axes[0].set_title(f"Reactivity Inserted Over Time | {transient.capitalize()} transient")
    axes[0].set_ylabel(r"Reactivity $\rho$ [Δk/k]")
    axes[0].grid(True, alpha=0.3)
    axes[0].axvline(onset_time, color="k", linestyle="--", alpha=0.35)

    axes[1].plot(macro_time, rod_height_macro, color="tab:green", linewidth=2.0)
    axes[1].set_title(f"{control_rod} Height Over Time")
    axes[1].set_ylabel("Control rod height [cm]")
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(onset_time, color="k", linestyle="--", alpha=0.35)

    for axis, series, title in group_specs:
        for point_idx, point_name in enumerate(POINTS_OF_INTEREST.keys()):
            axis.plot(micro_time, series[:, point_idx], linewidth=2.0, label=point_name)
        axis.set_title(f"Localized {title} at Three Points")
        axis.set_ylabel("Flux / flux(t0)")
        axis.grid(True, alpha=0.3)
        axis.legend(loc="best")
        axis.axvline(onset_time, color="k", linestyle="--", alpha=0.35)

    axes[1].set_xlabel("Time [s]")
    axes[2].set_xlabel("Time [s]")
    axes[3].set_xlabel("Time [s]")
    fig.suptitle(f"Localized Point Kinetics During a Short Control-Rod Insertion | {control_rod}")
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    if out_path is not None:
        fig.savefig(out_path, dpi=150, bbox_inches="tight")

    return fig, axes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track localized thermal and fast flux at three points during a small control-rod insertion transient.",
    )
    parser.add_argument("--transient", choices=TRANSIENT_MODES, default="ramp", help="Example-style reactivity transient to use.")
    parser.add_argument("--control-rod", choices=("CR1", "CR2"), default="CR1", help="Which control rod moves during the transient.")
    parser.add_argument("--t-final", type=float, default=10.0, help="Total simulation time in seconds.")
    parser.add_argument("--dt-macro", type=float, default=0.1, help="Macro step size in seconds.")
    parser.add_argument("--dt-micro", type=float, default=0.001, help="Micro step size in seconds.")
    parser.add_argument("--rod-start-height", type=float, default=50.0, help="Starting control rod height in cm.")
    parser.add_argument("--rod-insertion-cm", type=float, default=5.0, help="Total rod insertion distance in cm.")
    parser.add_argument(
        "--rod-insertion-duration",
        type=float,
        default=2.0,
        help="Duration of the rod insertion ramp in seconds.",
    )
    parser.add_argument("--step-onset", type=float, default=2.0, help="Step transient onset time in seconds.")
    parser.add_argument("--step-fraction", type=float, default=0.1, help="Step transient amplitude as a fraction of beta_total.")
    parser.add_argument("--ramp-start", type=float, default=2.0, help="Ramp transient start time in seconds.")
    parser.add_argument(
        "--ramp-slope-fraction",
        type=float,
        default=0.5,
        help="Ramp transient slope as a fraction of beta_total per second.",
    )
    parser.add_argument("--ramp-duration", type=float, default=2.0, help="Duration used to map ramp control-rod insertion to height.")
    parser.add_argument(
        "--sin-amplitude-fraction",
        type=float,
        default=0.3,
        help="Sinusoidal transient amplitude as a fraction of beta_total.",
    )
    parser.add_argument("--sin-period", type=float, default=25.0, help="Sinusoidal transient period in seconds.")
    parser.add_argument(
        "--fixed-cr2-height",
        type=float,
        default=None,
        help="Fixed height for the second control rod. Defaults to the starting rod height.",
    )
    parser.add_argument(
        "--dummy-water-density-multiplier",
        type=float,
        default=1.0,
        help="Nominal dummy-water density multiplier.",
    )
    parser.add_argument(
        "--fuel-assembly-water-density-multiplier",
        type=float,
        default=1.0,
        help="Nominal fuel-assembly water density multiplier.",
    )
    parser.add_argument(
        "--p0",
        type=float,
        default=1.0,
        help="Initial relative neutron density for the PRKE solver.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=HERE / "visualize_point_kinetics.png",
        help="Output image path for the combined thermal/fast point-kinetics figure.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _validate_points(POINTS_OF_INTEREST)

    fixed_cr2_height = args.rod_start_height if args.fixed_cr2_height is None else args.fixed_cr2_height
    result = simulate_point_kinetics(
        total_time=args.t_final,
        dt_macro=args.dt_macro,
        dt_micro=args.dt_micro,
        transient=args.transient,
        control_rod=args.control_rod,
        rod_start_height=args.rod_start_height,
        rod_insertion_cm=args.rod_insertion_cm,
        insertion_duration=args.rod_insertion_duration,
        fixed_cr2_height=fixed_cr2_height,
        dummy_water_density_multiplier=args.dummy_water_density_multiplier,
        fuel_assembly_water_density_multiplier=args.fuel_assembly_water_density_multiplier,
        step_onset=args.step_onset,
        step_fraction=args.step_fraction,
        ramp_start=args.ramp_start,
        ramp_slope_fraction=args.ramp_slope_fraction,
        ramp_duration=args.ramp_duration,
        sinusoidal_amplitude_fraction=args.sin_amplitude_fraction,
        sinusoidal_period=args.sin_period,
        p0=args.p0,
    )

    macro_times = np.asarray(result["macro_times"], dtype=float)
    micro_time = np.asarray(result["time"], dtype=float)
    reactivity_macro = np.asarray(result["reactivity_macro"], dtype=float)
    rod_height_macro = np.asarray(result["control_rod_height"], dtype=float)
    thermal_flux = np.asarray(result["thermal_flux"], dtype=float)
    fast_flux = np.asarray(result["fast_flux"], dtype=float)
    transient = str(result["transient"])
    control_rod = str(result["control_rod"])

    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plot_full_kinetics(
        macro_times,
        micro_time,
        reactivity_macro,
        rod_height_macro,
        thermal_flux,
        fast_flux,
        transient,
        control_rod,
        out_path,
    )

    print(f"Saved point-kinetics plot to {out_path}")

    plt.show()


if __name__ == "__main__":
    main()