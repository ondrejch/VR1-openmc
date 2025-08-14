#!/usr/bin/env python3
"""
VR1 Absorption Rod Example

This example demonstrates the absorption rod and control rod functionality
in VR1 reactor lattice configurations.

Features demonstrated:
- Fully withdrawn control rods ('O')
- Fully inserted control rods ('X')
- Variable absorption rod heights ('AR' prefix)
- Mixed lattice with control rods and fuel assemblies
- Source region handling with control rods
"""

import sys
import os

# Add vr1 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vr1.core import TestLattice
from vr1.settings import SettingsOpenMC
from vr1.lattice_units import IRT4M, AbsRod
from vr1.materials import vr1_materials

def main():
    print("VR1 OpenMC Absorption Rod Example")
    print("=" * 45)
    
    # Example 1: Direct absorption rod creation
    print("\n1. Creating absorption rod directly:")
    abs_rod = AbsRod(materials=vr1_materials, rod_height=25.0)
    print(f"✓ Absorption rod created: {abs_rod.name()}")
    print(f"✓ Rod height: {abs_rod.rod_height} cm")
    
    # Build the absorption rod universe
    abs_universe = abs_rod.build()
    print("✓ Absorption rod universe built successfully")
    
    # Example 2: Fuel assembly with absorption rod
    print("\n2. Creating 6-tube FA with absorption rod:")
    fa_with_abs = IRT4M(materials=vr1_materials, fa_type='6', abs_rod_height=15.0)
    print(f"✓ 6-tube FA with absorption rod created")
    print(f"✓ Absorption rod height: {fa_with_abs.abs_rod_height} cm")
    
    # Build the fuel assembly with absorption rod
    fa_abs_universe = fa_with_abs.build()
    print("✓ FA with absorption rod universe built successfully")
    
    # Example 3: Control rod positions in lattice
    print("\n3. Creating lattice with various control rod positions:")
    control_rod_config = [
        ['8', 'O', '6', 'X'],  # 8-tube FA, withdrawn rod, 6-tube FA, inserted rod
        ['O', 'w', 'w', 'O'],  # Withdrawn rods with water
        ['6', 'X', '8', '6'],  # Mixed FAs with inserted rod
        ['X', '4', 'O', 'X']   # Control rods with 4-tube FA
    ]
    
    print("Control rod configuration:")
    for i, row in enumerate(control_rod_config):
        print(f"  Row {i+1}: {row}")
    
    print("\nLegend:")
    print("  '8', '6', '4': Fuel assemblies (number of tubes)")
    print("  'O': Fully withdrawn control rod (84.7 cm)")
    print("  'X': Fully inserted control rod (0 cm)")
    print("  'w': Water cell")
    
    control_lattice = TestLattice(lattice_str=control_rod_config)
    print("✓ Control rod lattice created and formatted to 8x8")
    print(f"✓ Source region: {control_lattice.source_lower_left} to {control_lattice.source_upper_right}")
    
    # Example 4: Variable absorption rod heights
    print("\n4. Creating lattice with variable absorption rod heights:")
    variable_rod_config = [
        ['8', 'AR10.5', '6'],    # FA, rod at 10.5 cm, FA
        ['AR25.0', 'w', 'AR5.2'], # Rod at 25.0 cm, water, rod at 5.2 cm
        ['6', 'AR42.8', '8']     # FA, rod at 42.8 cm, FA
    ]
    
    print("Variable rod configuration:")
    for i, row in enumerate(variable_rod_config):
        print(f"  Row {i+1}: {row}")
    
    print("\nLegend:")
    print("  'AR{height}': Absorption rod at specific height in cm")
    print("  Example: 'AR10.5' = absorption rod inserted 10.5 cm")
    
    variable_lattice = TestLattice(lattice_str=variable_rod_config)
    print("✓ Variable absorption rod lattice created")
    
    # Example 5: Complete simulation setup with control rods
    print("\n5. Setting up complete simulation with control rods:")
    
    # Create a realistic control rod pattern
    realistic_config = [
        [8, 'O', 6, 'O', 8],     # Outer control rods withdrawn
        ['O', 6, 'X', 6, 'O'],   # Center control rod inserted
        [4, 'X', 8, 'X', 4],     # Safety rods inserted
        ['O', 6, 'X', 6, 'O'],   # Symmetric pattern
        [8, 'O', 6, 'O', 8]      # Outer control rods withdrawn
    ]
    
    print("Realistic control rod pattern (5x5):")
    for i, row in enumerate(realistic_config):
        print(f"  Row {i+1}: {row}")
    
    # Create lattice
    realistic_lattice = TestLattice(lattice_str=realistic_config)
    print("✓ Realistic control rod lattice created")
    
    # Create settings with source
    settings = SettingsOpenMC()
    source = settings.create_source(
        realistic_lattice.source_lower_left,
        realistic_lattice.source_upper_right,
        source_type='uniform'
    )
    print("✓ Neutron source created for control rod configuration")
    
    # Create settings.xml
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_file = settings.create_settings_xml(output_path=temp_dir)
        print(f"✓ Settings XML created: {settings_file}")
    
    # Example 6: Demonstrate rod worth calculation setup
    print("\n6. Control rod worth calculation setup:")
    
    # All rods out configuration
    all_out_config = [
        [8, 'O', 6, 'O', 8],
        ['O', 6, 'O', 6, 'O'], 
        [4, 'O', 8, 'O', 4],
        ['O', 6, 'O', 6, 'O'],
        [8, 'O', 6, 'O', 8]
    ]
    
    # All rods in configuration  
    all_in_config = [
        [8, 'X', 6, 'X', 8],
        ['X', 6, 'X', 6, 'X'],
        [4, 'X', 8, 'X', 4], 
        ['X', 6, 'X', 6, 'X'],
        [8, 'X', 6, 'X', 8]
    ]
    
    print("All rods OUT configuration created - for reference k-effective")
    lattice_out = TestLattice(lattice_str=all_out_config)
    
    print("All rods IN configuration created - for shutdown k-effective")
    lattice_in = TestLattice(lattice_str=all_in_config)
    
    print("✓ Both configurations ready for rod worth calculation")
    print("  Rod worth = k_eff(rods out) - k_eff(rods in)")
    
    print("\n" + "=" * 45)
    print("Absorption rod example completed successfully!")
    print("\nKey features demonstrated:")
    print("- Direct AbsRod class usage")
    print("- IRT4M fuel assemblies with absorption rods") 
    print("- Control rod positions ('O' and 'X')")
    print("- Variable absorption rod heights ('AR{height}')")
    print("- Realistic control rod patterns")
    print("- Rod worth calculation setup")
    print("\nThe absorption rod implementation supports:")
    print("- Vertical geometry extension to rod tip")
    print("- Proper surface definitions (ABS.1-ABS.5)")
    print("- Variable rod insertion heights")
    print("- Integration with lattice framework")

if __name__ == "__main__":
    main()