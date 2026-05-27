#!/usr/bin/env python3
"""
Thermal Power Time Series Analyzer

Extracts and visualizes thermal power evolution over time at a specific (x, y, z) location.
Useful for studying how control rod insertion/withdrawal affects local power.

Usage:
    python power_timeseries.py --x 30 --y 30 --z 35
    python power_timeseries.py --x 25 --y 25 --z 20 --save plot.png
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from digital_twin_files.rom.digital_twin import reshape_flux_vector


def load_results(results_path="coupled_digital_twin_results.npz"):
    """Load coupled digital twin results."""
    path = Path(results_path)
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}. Run digital_twin_driver.py first.")
    
    results = np.load(path)
    return {
        "localized_power": results["localized_power"],
        "time": results["time"],
    }


def extract_timeseries(localized_power, macro_time, x: int, y: int, z: int):
    """
    Extract thermal power time series at a specific (x, y, z) location.
    
    Parameters
    ----------
    localized_power : ndarray of shape (n_frames, n_mesh_elements)
        Flattened localized power for each macro frame
    macro_time : ndarray of shape (n_frames,)
        Time for each macro frame (seconds)
    x, y, z : int
        Mesh indices (0-indexed)
    
    Returns
    -------
    time : ndarray
        Time array (seconds)
    power : ndarray
        Thermal power at (x, y, z) for each frame
    amplitude : ndarray
        Max power at (x, y, z) for each frame (for normalization tracking)
    """
    time = macro_time.copy()
    power = np.zeros(localized_power.shape[0])
    amplitude = np.zeros(localized_power.shape[0])
    
    for frame_idx in range(localized_power.shape[0]):
        # Reshape flattened vector to 4D mesh
        field = reshape_flux_vector(localized_power[frame_idx])
        
        # Extract thermal group (group 0) at (z, y, x)
        power[frame_idx] = field[z, y, x, 0]
        amplitude[frame_idx] = np.max(field[:, :, :, 0])
    
    return time, power, amplitude


def plot_timeseries(time, power, amplitude, x: int, y: int, z: int, save_path=None):
    """Plot thermal power time series with annotations."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Raw power time series
    ax1.plot(time, power, 'o-', linewidth=2, markersize=4, color='#ff7f0e')
    ax1.set_xlabel("Time (s)", fontsize=12)
    ax1.set_ylabel("Thermal Power (log scale)", fontsize=12)
    ax1.set_yscale('log')
    ax1.set_title(f"Local Thermal Power vs. Time at (x={x}, y={y}, z={z})", fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, which='both')
    
    # Normalized power (to show shape changes independent of global amplitude)
    normalized_power = power / (amplitude + 1e-12)
    ax2.plot(time, normalized_power, 's-', linewidth=2, markersize=4, color='#2ca02c')
    ax2.set_xlabel("Time (s)", fontsize=12)
    ax2.set_ylabel("Normalized Power (local / global max)", fontsize=12)
    ax2.set_title("Normalized Local Power (removes global amplitude trend)", fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Plot saved to: {save_path}")
    
    plt.show()


def print_summary(time, power, amplitude, x: int, y: int, z: int):
    """Print summary statistics."""
    normalized_power = power / (amplitude + 1e-12)
    
    print("\n" + "="*70)
    print(f"  THERMAL POWER TIME SERIES ANALYSIS")
    print(f"  Location: (x={x}, y={y}, z={z})")
    print("="*70)
    print(f"\nTime range:           {time[0]:.4f} – {time[-1]:.4f} s")
    print(f"Number of frames:     {len(time)}")
    print(f"\nRaw Power Statistics:")
    print(f"  Min:                {np.min(power):.4e}")
    print(f"  Max:                {np.max(power):.4e}")
    print(f"  Mean:               {np.mean(power):.4e}")
    print(f"  Std Dev:            {np.std(power):.4e}")
    print(f"\nNormalized Power (local / max global):")
    print(f"  Min:                {np.min(normalized_power):.6f}")
    print(f"  Max:                {np.max(normalized_power):.6f}")
    print(f"  Mean:               {np.mean(normalized_power):.6f}")
    print(f"  Std Dev:            {np.std(normalized_power):.6f}")
    
    # Find peaks and valleys
    peak_frame = np.argmax(power)
    valley_frame = np.argmin(power)
    print(f"\nPeak power at frame {peak_frame}: {power[peak_frame]:.4e} at t={time[peak_frame]:.4f} s")
    print(f"Minimum power at frame {valley_frame}: {power[valley_frame]:.4e} at t={time[valley_frame]:.4f} s")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract and visualize thermal power at a specific mesh location over time.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View power at center location
  python power_timeseries.py --x 30 --y 30 --z 35
  
  # View power at control rod location (approximately x=25-30, y=25-30, z=9-55)
  python power_timeseries.py --x 27 --y 27 --z 30
  
  # Save plot to file
  python power_timeseries.py --x 30 --y 30 --z 35 --save power_history.png
        """
    )
    
    parser.add_argument('--x', type=int, default=30, help='X mesh index (0-59)')
    parser.add_argument('--y', type=int, default=30, help='Y mesh index (0-59)')
    parser.add_argument('--z', type=int, default=35, help='Z mesh index (0-69)')
    parser.add_argument('--results', type=Path, default=HERE / 'coupled_digital_twin_results.npz',
                       help='Path to results file')
    parser.add_argument('--save', type=Path, default=None,
                       help='Save plot to this file (e.g., plot.png)')
    
    args = parser.parse_args()
    
    # Load data
    results = load_results(args.results)
    localized_power = results["localized_power"]
    macro_time = results["time"]
    
    # Validate indices
    field_shape = reshape_flux_vector(localized_power[0]).shape
    if not (0 <= args.x < field_shape[2] and 0 <= args.y < field_shape[1] and 0 <= args.z < field_shape[0]):
        print(f"Error: Invalid indices. Mesh shape is {field_shape} (z, y, x, groups)")
        print(f"  x must be in [0, {field_shape[2]-1}]")
        print(f"  y must be in [0, {field_shape[1]-1}]")
        print(f"  z must be in [0, {field_shape[0]-1}]")
        return
    
    # Extract time series
    time, power, amplitude = extract_timeseries(localized_power, macro_time, args.x, args.y, args.z)
    
    # Print summary
    print_summary(time, power, amplitude, args.x, args.y, args.z)
    
    # Plot
    plot_timeseries(time, power, amplitude, args.x, args.y, args.z, save_path=args.save)


if __name__ == "__main__":
    main()
