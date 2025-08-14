#!/usr/bin/env python3
"""
Basic VR1 Lattice Example

This example demonstrates the basic functionality of creating VR1 reactor lattice
configurations with automatic formatting and source definition.

Features demonstrated:
- Creating lattice with integer inputs (auto-converted to strings)
- Automatic 8x8 grid formatting
- Source region definition
- Settings.xml creation
"""

import sys
import os

# Add vr1 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vr1.core import TestLattice, FuelAssembly
from vr1.settings import SettingsOpenMC

def main():
    print("VR1 OpenMC Basic Lattice Example")
    print("=" * 40)
    
    # Example 1: Simple 3x3 configuration with integer inputs
    print("\n1. Creating 3x3 lattice configuration with integer inputs:")
    simple_config = [
        [8, 4, 8],  # 8-tube FA, 4-tube FA, 8-tube FA
        [6, 'w', 6], # 6-tube FA, water, 6-tube FA
        [4, 8, 4]   # 4-tube FA, 8-tube FA, 4-tube FA
    ]
    
    print(f"Input configuration: {simple_config}")
    
    # Create lattice - integers will be auto-converted to strings
    lattice = TestLattice(lattice_str=simple_config)
    print("✓ Lattice created successfully with auto-conversion")
    print(f"✓ Source region: {lattice.source_lower_left} to {lattice.source_upper_right}")
    
    # Example 2: Single fuel assembly
    print("\n2. Creating individual fuel assembly:")
    fa8 = FuelAssembly('8')  # 8-tube fuel assembly
    print(f"✓ 8-tube fuel assembly created: {fa8.fa_type}")
    print(f"✓ FA source region: {fa8.source_lower_left} to {fa8.source_upper_right}")
    
    # Example 3: Settings and source creation
    print("\n3. Creating simulation settings and neutron source:")
    settings = SettingsOpenMC()
    
    # Create uniform source over lattice active region
    source = settings.create_source(
        lattice.source_lower_left,
        lattice.source_upper_right,
        source_type='uniform'
    )
    print("✓ Uniform neutron source created")
    print(f"✓ Source spans: {lattice.source_lower_left} to {lattice.source_upper_right}")
    
    # Create settings.xml file
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_file = settings.create_settings_xml(output_path=temp_dir)
        print(f"✓ Settings XML created: {settings_file}")
    
    # Example 4: Larger configuration
    print("\n4. Creating larger 5x4 configuration:")
    larger_config = [
        [8, 6, 4, 6, 8],
        [6, 'w', 8, 'w', 6], 
        [4, 8, 6, 8, 4],
        ['w', 6, 4, 6, 'w']
    ]
    
    print(f"Input configuration: {larger_config}")
    larger_lattice = TestLattice(lattice_str=larger_config)
    print("✓ Larger lattice created and automatically formatted to 8x8")
    
    # Example 5: Water-only configuration
    print("\n5. Creating water-only (reflector) configuration:")
    water_config = [['w']]  # Single water cell
    water_lattice = TestLattice(lattice_str=water_config)
    print("✓ Water lattice created - automatically padded to 8x8")
    
    print("\n" + "=" * 40)
    print("Basic example completed successfully!")
    print("\nKey features demonstrated:")
    print("- Integer to string auto-conversion")
    print("- Automatic lattice padding to 8x8 grid")
    print("- Source region calculation")
    print("- Settings.xml creation")
    print("- Flexible lattice configurations")

if __name__ == "__main__":
    main()