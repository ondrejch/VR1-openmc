#!/usr/bin/env python3
"""
Control Rod Insertion/Ejection Analysis

Visualizes neutron kinetics response during control rod movements.
Shows reactivity steps, neutron density, and localized power at control rod location
during insertion/ejection events, similar to PKE solver examples.

Usage:
    python rod_insertion_analysis.py
    python rod_insertion_analysis.py --save rod_event.png
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
        "time": results["time"],
        "reactivity_macro": results["reactivity_macro"],
        "neutron_density": results["neutron_density"],
        "localized_power": results["localized_power"],
    }


def find_rod_events(reactivity, time, threshold=0.0001):
    """
    Find frames with significant reactivity changes (rod insertion/ejection events).
    
    Parameters
    ----------
    reactivity : ndarray
        Reactivity values at each frame
    time : ndarray
        Time at each frame
    threshold : float
        Minimum |Δρ/Δt| to identify as an event (1/s)
    
    Returns
    -------
    event_frames : list of int
        Frame indices with significant reactivity changes
    event_times : list of float
        Time values at those frames
    event_rates : list of float
        Rate of reactivity change (1/s) at those frames
    """
    drho_dt = np.gradient(reactivity, time)
    event_frames = np.where(np.abs(drho_dt) > threshold)[0]
    event_times = time[event_frames]
    event_rates = drho_dt[event_frames]
    
    return event_frames, event_times, event_rates


def extract_rod_location(localized_power):
    """
    Estimate control rod center location from power depression.
    Finds the (x, y, z) with minimum average power (approximate).
    
    Parameters
    ----------
    localized_power : ndarray of shape (n_frames, n_mesh_elements)
        Localized power for each frame
    
    Returns
    -------
    x, y, z : int
        Approximate rod center (mesh indices)
    """
    # Use first frame to estimate rod location
    field = reshape_flux_vector(localized_power[0])
    thermal = field[:, :, :, 0]
    
    # Average over z (axial) to find x-y center
    xy_avg = np.mean(thermal, axis=0)
    y_min, x_min = np.unravel_index(np.argmin(xy_avg), xy_avg.shape)
    
    # Find z with maximum power suppression
    xz_slice = thermal[:, y_min, x_min]
    z_center = np.argmax(xz_slice)  # Peak suppression
    
    return int(x_min), int(y_min), int(z_center)


def extract_power_timeseries(localized_power, x: int, y: int, z: int):
    """Extract power at specific location over all frames."""
    power = np.zeros(localized_power.shape[0])
    for frame_idx in range(localized_power.shape[0]):
        field = reshape_flux_vector(localized_power[frame_idx])
        power[frame_idx] = field[z, y, x, 0]
    return power


def plot_rod_events(time, reactivity, neutron_density, localized_power, save_path=None):
    """Create comprehensive rod insertion/ejection analysis plot."""
    
    # Find rod events
    event_frames, event_times, event_rates = find_rod_events(reactivity, time, threshold=0.0001)
    
    # Estimate rod location
    x_rod, y_rod, z_rod = extract_rod_location(localized_power)
    rod_power = extract_power_timeseries(localized_power, x_rod, y_rod, z_rod)
    
    print(f"\nControl Rod Location (estimated): x={x_rod}, y={y_rod}, z={z_rod}")
    print(f"Found {len(event_frames)} significant rod movement events")
    if len(event_frames) > 0:
        print(f"  Max reactivity rate: {np.max(np.abs(event_rates)):.6f} 1/s")
        print(f"  Event times: {event_times}")
    
    # Create figure
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(4, 1, hspace=0.35)
    
    # Plot 1: Reactivity with event markers
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(time, reactivity, 'b-', linewidth=2, label='Reactivity ρ(t)')
    if len(event_frames) > 0:
        ax1.plot(time[event_frames], reactivity[event_frames], 'ro', markersize=8, label='Rod events')
    ax1.set_ylabel('Reactivity (1/$)', fontsize=11)
    ax1.set_title('Control Rod Movement Events: Reactivity, Neutron Density, and Power Response', 
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # Plot 2: Neutron density (log scale)
    ax2 = fig.add_subplot(gs[1])
    ax2.semilogy(time, neutron_density, 'g-', linewidth=2, label='Neutron density P(t)')
    if len(event_frames) > 0:
        ax2.plot(time[event_frames], neutron_density[event_frames], 'ro', markersize=8)
    ax2.set_ylabel('Neutron Density (log scale)', fontsize=11)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend(fontsize=10)
    
    # Plot 3: Power at rod location (log scale)
    ax3 = fig.add_subplot(gs[2])
    ax3.semilogy(time, rod_power, color='#ff7f0e', linewidth=2, label=f'Power at rod (x={x_rod}, y={y_rod}, z={z_rod})')
    if len(event_frames) > 0:
        ax3.plot(time[event_frames], rod_power[event_frames], 'ro', markersize=8)
    ax3.set_ylabel('Local Power (log scale)', fontsize=11)
    ax3.grid(True, alpha=0.3, which='both')
    ax3.legend(fontsize=10)
    
    # Plot 4: Reactivity rate (dρ/dt) to highlight insertion/ejection ramps
    ax4 = fig.add_subplot(gs[3])
    drho_dt = np.gradient(reactivity, time)
    ax4.plot(time, drho_dt, 'purple', linewidth=2, label='dρ/dt (rod speed indicator)')
    if len(event_frames) > 0:
        ax4.plot(time[event_frames], drho_dt[event_frames], 'ro', markersize=8)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.set_xlabel('Time (s)', fontsize=11)
    ax4.set_ylabel('Reactivity Rate (1/s²)', fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Plot saved to: {save_path}")
    
    plt.show()


def print_summary(time, reactivity, neutron_density, localized_power):
    """Print summary of rod events."""
    event_frames, event_times, event_rates = find_rod_events(reactivity, time, threshold=0.0001)
    
    print("\n" + "="*70)
    print("  CONTROL ROD INSERTION/EJECTION ANALYSIS")
    print("="*70)
    print(f"\nTotal simulation time: {time[0]:.2f} – {time[-1]:.2f} s ({len(time)} frames)")
    print(f"Macro time step: {time[1] - time[0]:.4f} s")
    
    print(f"\nReactivity Statistics:")
    print(f"  Range:  {np.min(reactivity):.6f} to {np.max(reactivity):.6f} $")
    print(f"  Change: {reactivity[-1] - reactivity[0]:.6f} $ (Δρ)")
    
    print(f"\nNeutron Density Statistics:")
    print(f"  Min:    {np.min(neutron_density):.4e}")
    print(f"  Max:    {np.max(neutron_density):.4e}")
    print(f"  Ratio:  {np.max(neutron_density) / np.min(neutron_density):.2e}x")
    
    print(f"\nRod Events (|dρ/dt| > 0.0001 1/s):")
    if len(event_frames) > 0:
        print(f"  Count:  {len(event_frames)} events")
        print(f"  Max rate: {np.max(np.abs(event_rates)):.6f} 1/s²")
        print(f"  Event times: {event_times}")
    else:
        print(f"  No significant rod movement detected")
    
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and visualize control rod insertion/ejection events and neutron kinetics response."
    )
    parser.add_argument('--results', type=Path, default=HERE / 'coupled_digital_twin_results.npz',
                       help='Path to results file')
    parser.add_argument('--save', type=Path, default=None,
                       help='Save plot to this file (e.g., rod_events.png)')
    
    args = parser.parse_args()
    
    # Load results
    results = load_results(args.results)
    
    # Print summary
    print_summary(results["time"], results["reactivity_macro"], 
                 results["neutron_density"], results["localized_power"])
    
    # Create plots
    plot_rod_events(results["time"], results["reactivity_macro"], 
                   results["neutron_density"], results["localized_power"],
                   save_path=args.save)


if __name__ == "__main__":
    main()
