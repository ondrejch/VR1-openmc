"""Create an animation (GIF/MP4) of the thermal localized power slice over time.

Loads `coupled_digital_twin_results.npz` (or another NPZ with the same keys)
and animates the thermal slice at a chosen Z-index. Saves to GIF by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

from digital_twin import reshape_flux_vector


def make_animation(results_path: Path, out_path: Path, z_index: int = 35, interval_ms: int = 500):
    data = np.load(results_path)
    if 'localized_power' not in data:
        raise KeyError('NPZ does not contain "localized_power" key')

    localized_power = data['localized_power']  # shape: (n_frames, n_cells)
    n_frames = localized_power.shape[0]

    # Build the thermal 2D frames (Z, Y, X, Energy) -> take group 0
    frames = []
    for i in range(n_frames):
        full_field = reshape_flux_vector(localized_power[i])
        thermal = full_field[z_index, :, :, 0]
        frames.append(thermal)

    vmin = min(np.nanmin(f) for f in frames)
    vmax = max(np.nanmax(f) for f in frames)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(frames[0], origin='lower', cmap='inferno', vmin=vmin, vmax=vmax)
    ax.set_title(f'Thermal Localized Power (z={z_index})')
    ax.set_xlabel('X index')
    ax.set_ylabel('Y index')
    cbar = fig.colorbar(im, ax=ax, label='Arbitrary units')

    def update(frame_idx):
        im.set_data(frames[frame_idx])
        ax.set_title(f'Thermal Localized Power (z={z_index}) | t_idx={frame_idx}')
        return (im,)

    ani = animation.FuncAnimation(fig, update, frames=n_frames, blit=True, interval=interval_ms)

    # Try PillowWriter (GIF) first, fallback to FFMpegWriter (mp4) if available
    try:
        from matplotlib.animation import PillowWriter

        writer = PillowWriter(fps=max(1, int(1000 / interval_ms)))
        ani.save(out_path, writer=writer)
    except Exception:
        try:
            from matplotlib.animation import FFMpegWriter

            writer = FFMpegWriter(fps=max(1, int(1000 / interval_ms)))
            ani.save(out_path, writer=writer)
        except Exception as exc:
            raise RuntimeError(f"Failed to save animation: {exc}")

    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser(description='Animate thermal localized power from NPZ results')
    p.add_argument('--results', type=Path, default=Path('coupled_digital_twin_results.npz'))
    p.add_argument('--out', type=Path, default=Path('thermal_power_animation.gif'))
    p.add_argument('--z-index', type=int, default=35)
    p.add_argument('--interval-ms', type=int, default=500)
    return p.parse_args()


def main():
    args = parse_args()
    make_animation(args.results, args.out, z_index=args.z_index, interval_ms=args.interval_ms)
    print(f"Saved animation to {args.out}")


if __name__ == '__main__':
    main()
