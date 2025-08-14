#!/usr/bin/env python3

"""
    VR1 OpenMC Simulation Setup Script
    The script creates a VR1 reactor model with a configurable lattice design,
    full facility geometry including shielding and channels, and settings.
"""

import os
import sys

# Set up environment variables for OpenMC
os.environ["DYLD_LIBRARY_PATH"] = "/usr/local/lib:/usr/local/opt/libomp/lib:/usr/local/opt/hdf5/lib"
os.environ["OPENMC_CROSS_SECTIONS"] = "/Users/sa39262-admin/xs_data/endfb-viii.0-hdf5/cross_sections.xml"
os.environ['PYTHONPATH'] = '/Users/sa39262-admin/Documents/modeling/vr1-openmc'

# Add project path for imports
sys.path.append('/Users/sa39262-admin/Documents/modeling/vr1-openmc')

# Import required modules
import openmc
import matplotlib.pyplot as plt

from vr1.core import TestLattice
from vr1.materials import VR1Materials
from vr1.VR1facility import Facility
from vr1.settings import SettingsOpenMC

def create_vr1_simulation(output_dir='.', lattice_config=None):
    """
    Create complete VR1 reactor simulation with all XML files
    
    Parameters:
    - output_dir: Directory to write XML files (default: current directory)
    - lattice_config: Custom lattice configuration (default: predefined test lattice)
    
    Returns:
    - Dictionary with paths to generated XML files
    """
    
    print("=" * 60)
    print("VR1 OpenMC Simulation Setup")
    print("=" * 60)
    
    # Step 1: Create materials
    print("\n1. Creating VR1 materials...")
    materials = VR1Materials()
    mats = materials.get_materials()
    
    # Export materials.xml
    materials_file = os.path.join(output_dir, 'materials.xml')
    mats.export_to_xml(materials_file)
    print(f"   ✓ Materials XML exported to: {materials_file}")
    
    # Step 2: Create lattice configuration
    print("\n2. Creating reactor lattice...")
    if lattice_config is None:
        # Default test configuration from notebook
        lattice_config = [
            ["6", "6"],
            ["6", "8"], 
            ["4", "6"]
        ]
    
    print(f"   Lattice configuration:")
    for i, row in enumerate(lattice_config):
        print(f"     Row {i+1}: {row}")
    
    # Create TestLattice (will auto-format to 8x8 and convert integers to strings)
    lattice = TestLattice(materials, lattice_config)
    print(f"   ✓ Lattice created and formatted to 8x8 grid")
    print(f"   ✓ Source region: {lattice.source_lower_left} to {lattice.source_upper_right}")
    
    # Step 3: Create facility geometry
    print("\n3. Creating VR1 facility geometry...")
    facility = Facility(materials=materials)
    facility_universe = facility.build(lattice)
    print(f"   ✓ Facility geometry built with integrated lattice")
    
    # Step 4: Create and export geometry
    print("\n4. Exporting geometry...")
    geo = openmc.Geometry(root=facility_universe)
    geometry_file = os.path.join(output_dir, 'geometry.xml')
    geo.export_to_xml(geometry_file)
    print(f"   ✓ Geometry XML exported to: {geometry_file}")
    
    # Create model for settings
    mod = openmc.Model()
    mod.geometry = geo
    
    # Step 5: Create simulation settings with neutron source
    print("\n5. Creating simulation settings...")
    settings = SettingsOpenMC(
        name='VR1 Reactor Simulation',
        xs_lib='endf8.0',  # Using ENDF/B-VIII.0 as specified in environment
        xs_xml_root_path='/Users/sa39262-admin/xs_data'
    )
    
    # Create source and export settings.xml automatically
    settings_file = settings.setup_simulation(
        lattice=lattice,
        output_path=output_dir,
        source_type='uniform'
    )
    
    # Step 6: Create plots for visualization
    print("\n6. Creating visualization plots...")
    try:
        from vr1.plots import PlotManager
        
        plot_settings = {
            'resolution': 1000,
            # Customize plot definitions if needed
        }
        
        plot_manager = PlotManager(mod, plot_settings)
        plot_manager.run_and_display(display_plots=False)  # Don't display inline
        print("   ✓ Visualization plots created")
        
    except Exception as e:
        print(f"   ! Plot creation failed (non-critical): {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VR1 Simulation Setup Complete!")
    print("=" * 60)
    
    xml_files = {
        'materials': materials_file,
        'geometry': geometry_file, 
        'settings': settings_file
    }
    
    print("\nGenerated XML files:")
    for xml_type, filepath in xml_files.items():
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ {xml_type.capitalize():12} : {filepath} ({file_size:,} bytes)")
        else:
            print(f"  ✗ {xml_type.capitalize():12} : {filepath} (NOT FOUND)")
    
    print(f"\nSimulation parameters:")
    print(f"  Particles per generation: {settings.parm['npg']:,}")
    print(f"  Total generations:        {settings.parm['gen']:,}")
    print(f"  Skip generations:         {settings.parm['nsk']:,}")
    print(f"  Cross sections:           {settings.xs_lib}")
    
    print(f"\nTo run the simulation:")
    print(f"  cd {output_dir}")
    print(f"  openmc")
    
    return xml_files

def main():
    """Main function to create VR1 simulation setup"""
    
    # You can customize the lattice configuration here
    # Example configurations:
    
    # Original notebook configuration
    notebook_config = [
        ["6", "6"],
        ["6", "8"],
        ["4", "6"]
    ]
    
    # Alternative larger configuration with control rods
    # control_rod_config = [
    #     [8, 'O', 6, 'X'],  # 8-tube FA, withdrawn rod, 6-tube FA, inserted rod  
    #     ['O', 'w', 'w', 'O'],  # Withdrawn rods with water
    #     [6, 'X', 8, 6],   # Mixed FAs with inserted rod
    # ]
    
    # Alternative mixed configuration
    # mixed_config = [
    #     [8, 4, 8],
    #     [6, 'w', 6], 
    #     [4, 8, 4]
    # ]
    
    # Create simulation with notebook configuration
    try:
        xml_files = create_vr1_simulation(
            output_dir='.',  # Current directory (scratch/soha)
            lattice_config=notebook_config
        )
        
        print("\n" + "=" * 60)
        print("SUCCESS: All XML files generated successfully!")
        print("The VR1 reactor simulation is ready to run.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: Failed to create simulation setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()