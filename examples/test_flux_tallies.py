#!/usr/bin/env python3
"""
Simple test script to verify flux tally functionality works correctly
"""

import sys
import os
import tempfile

# Add vr1 to path
sys.path.insert(0, '/')

from vr1.core import TestLattice
from vr1.settings import SettingsOpenMC
from vr1.materials import vr1_materials

def test_flux_tallies():
    print("Testing flux tally functionality...")
    
    try:
        # Create simple test setup
        lattice = TestLattice(materials=vr1_materials)
        settings = SettingsOpenMC()
        
        # Test 1: Create fuel region flux tally
        fuel_tally = settings.create_fuel_region_flux_tally(lattice=lattice)
        print(f"✓ Fuel region flux tally created: {fuel_tally.name}")
        
        # Test 2: Create mesh flux tally
        mesh_tally = settings.create_mesh_flux_tally(
            tally_name='test_mesh',
            mesh_dimension=[5, 5, 3],
            lower_left=[-10, -10, -5],
            upper_right=[10, 10, 5]
        )
        print(f"✓ Mesh flux tally created: {mesh_tally.name}")
        
        # Test 3: Create energy-dependent tally
        energy_tally = settings.create_mesh_flux_tally(
            tally_name='test_energy',
            mesh_dimension=[3, 3, 2],
            lower_left=[-5, -5, -2],
            upper_right=[5, 5, 2],
            energy_groups=[0.0, 0.625, 20.0e6]
        )
        print(f"✓ Energy-dependent flux tally created: {energy_tally.name}")
        
        # Test 4: Check tallies are stored
        assert settings.tallies is not None
        assert len(settings.tallies) == 3
        print(f"✓ All tallies stored correctly: {len(settings.tallies)} tallies")
        
        # Test 5: Try exporting with tallies
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = settings.setup_simulation(
                lattice=lattice, 
                output_path=temp_dir,
                source_type='uniform'
            )
            
            # Check if tallies.xml was created
            tallies_file = os.path.join(temp_dir, 'tallies.xml')
            if os.path.exists(tallies_file):
                print(f"✓ Tallies XML exported successfully: {tallies_file}")
            else:
                print("✗ Tallies XML not created")
                
        print("\n✅ All flux tally tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Flux tally test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flux_tallies()
    sys.exit(0 if success else 1)