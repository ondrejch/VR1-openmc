"""Animate a short-time point-kinetics transient to show prompt and delayed neutron effects.

This script uses the VR-1 PRKE micro-stepper directly and creates a GIF of the
relative neutron density / normalized power response to a step reactivity insertion.
It is intended for short time scales where prompt jump and delayed neutron growth
are visible.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.ticker import ScalarFormatter
import numpy as np

from digital_twin_driver import PRKEMicroStepper, thermal_default_params


def simulate_step_transient(
    t_final: float,
    dt: float,
    rho_step: float,
    p0: float = 1.0,
    params: dict[str, np.ndarray | float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate a step-reactivity transient using the PRKE micro-stepper."""

    if params is None:
        params = thermal_default_params

    stepper = PRKEMicroStepper(params=params, p0=p0)
    times = [0.0]
    neutron_density = [float(stepper.state.neutron_density)]

    def rho_of_t(t: float) -> float:
        return float(rho_step if t >= 0.0 else 0.0)

    elapsed = 0.0
    while elapsed < t_final:
        dt_step = min(dt, t_final - elapsed)
        stepper.step_rk4(dt_step, rho_of_t, elapsed)
        elapsed += dt_step
        times.append(elapsed)
        neutron_density.append(float(stepper.state.neutron_density))

    times = np.asarray(times, dtype=float)
    neutron_density = np.asarray(neutron_density, dtype=float)
    normalized_power = neutron_density / neutron_density[0]
    return times, neutron_density, normalized_power


def make_animation(
    out_path: Path,
    t_final: float = 0.2,
    dt: float = 1e-4,
    rho_step: float = 0.003,
    interval_ms: int = 20,
    frame_stride: int = 20,
    zoom_window: float = 0.005,
) -> None:
    """Create a GIF that shows the kinetics-driven power change over time."""

    times, neutron_density, normalized_power = simulate_step_transient(t_final, dt, rho_step)
    frame_indices = np.arange(0, len(times), max(1, frame_stride), dtype=int)
    if frame_indices[-1] != len(times) - 1:
        frame_indices = np.append(frame_indices, len(times) - 1)

    beta_total = float(np.sum(thermal_default_params["beta"]))
    prompt_jump_estimate = beta_total / max(beta_total - rho_step, 1e-12)

    fig, (ax_curve, ax_zoom) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [2.1, 1.2]})

    ax_curve.set_title("Short-Time PRKE Response")
    ax_curve.set_xlabel("Time [s]")
    ax_curve.set_ylabel("Relative neutron density / power")
    ax_curve.set_yscale("log")
    ax_curve.yaxis.set_major_formatter(ScalarFormatter())
    ax_curve.grid(True, which="both", alpha=0.3)

    x_max = max(times[-1], 1e-6)
    y_min = max(min(np.min(normalized_power), prompt_jump_estimate) * 0.8, 1e-6)
    y_max = max(np.max(normalized_power), prompt_jump_estimate) * 1.2
    ax_curve.set_xlim(0.0, x_max)
    ax_curve.set_ylim(y_min, y_max)

    line, = ax_curve.plot([], [], color="tab:blue", lw=2)
    marker, = ax_curve.plot([], [], marker="o", color="tab:red", ms=6)
    prompt_line = ax_curve.axhline(prompt_jump_estimate, color="tab:green", ls="--", lw=1.5, label="Prompt jump estimate")
    ax_curve.legend(loc="best")

    ax_zoom.set_title("Prompt-Jump Zoom")
    ax_zoom.set_xlabel("Time [s]")
    ax_zoom.set_ylabel("Relative neutron density / power")
    ax_zoom.grid(True, which="both", alpha=0.3)
    ax_zoom.set_xlim(0.0, max(zoom_window, dt))
    ax_zoom.set_ylim(max(0.9, y_min), min(max(2.5, y_max), 5.0))
    zoom_line, = ax_zoom.plot([], [], color="tab:orange", lw=2)
    zoom_marker, = ax_zoom.plot([], [], marker="o", color="tab:red", ms=6)
    zoom_prompt_line = ax_zoom.axhline(prompt_jump_estimate, color="tab:green", ls="--", lw=1.5)
    ax_zoom.text(
        0.02,
        0.95,
        "Prompt jump should appear here\nwithin the first few ms.",
        transform=ax_zoom.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.75},
    )

    def update(frame_number: int):
        sample_idx = int(frame_indices[frame_number])
        line.set_data(times[: sample_idx + 1], normalized_power[: sample_idx + 1])
        marker.set_data([times[sample_idx]], [normalized_power[sample_idx]])
        zoom_mask = times <= zoom_window
        zoom_line.set_data(times[zoom_mask], normalized_power[zoom_mask])
        zoom_marker.set_data([times[sample_idx]], [normalized_power[sample_idx]])
        return line, marker, prompt_line, zoom_line, zoom_marker, zoom_prompt_line

    fig.suptitle(
        f"Short-Time PRKE Response | t_final={t_final:.3f} s | rho_step={rho_step:.4f} | beta_total={beta_total:.5f}",
        fontsize=12,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    ani = animation.FuncAnimation(fig, update, frames=len(frame_indices), interval=interval_ms, blit=True)

    try:
        from matplotlib.animation import PillowWriter

        writer = PillowWriter(fps=max(1, int(1000 / interval_ms)))
        ani.save(out_path, writer=writer)
    except Exception as exc:
        raise RuntimeError(f"Failed to save short kinetics animation: {exc}")

    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Animate a short PRKE transient to show prompt/delayed neutron power response.")
    parser.add_argument("--out", type=Path, default=Path("short_kinetics_animation.gif"))
    parser.add_argument("--t-final", type=float, default=0.2, help="Final simulation time in seconds.")
    parser.add_argument("--dt", type=float, default=1e-4, help="Integration step size in seconds.")
    parser.add_argument("--rho-step", type=float, default=0.003, help="Step reactivity insertion in delta-k/k.")
    parser.add_argument("--interval-ms", type=int, default=20, help="Frame interval in milliseconds.")
    parser.add_argument("--frame-stride", type=int, default=20, help="Plot every Nth integrated point in the GIF.")
    parser.add_argument("--zoom-window", type=float, default=0.005, help="Early-time window in seconds for the prompt-jump zoom panel.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    make_animation(
        args.out,
        t_final=args.t_final,
        dt=args.dt,
        rho_step=args.rho_step,
        interval_ms=args.interval_ms,
        frame_stride=args.frame_stride,
        zoom_window=args.zoom_window,
    )
    print(f"Saved short kinetics animation to {args.out}")


if __name__ == "__main__":
    main()
