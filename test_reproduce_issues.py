#!/usr/bin/env python3
"""
Test script to reproduce issues described in the repository.
This helps understand current functionality and identify problems.
"""

import os
import sys
sys.path.insert(0, 'vr1')

from vr1.core import TestLattice, core_designs
from vr1.settings import SettingsOpenMC
from vr1.materials import vr1_materials

def test_lattice_reformatter():
    """Test Issue #1: Lattice reformatter with 8+ elements"""
    print("=== Testing Lattice Reformatter ===")
    
    # Test case with exactly 8 elements (should work now)
    test_8_elements = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]
    
    # Test case with more than 8 elements (should fail)
    test_9_elements = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
    
    lattice = TestLattice()
    
    try:
        result_8 = lattice.reformat(test_8_elements)
        print(f"✓ 8 elements test passed: {len(result_8[0])} elements in first row")
    except Exception as e:
        print(f"✗ 8 elements test failed: {e}")
        
    try:
        result_9 = lattice.reformat(test_9_elements)
        print(f"✗ 9 elements test should have failed but didn't")
    except ValueError as e:
        print(f"✓ 9 elements test correctly failed: {e}")
    except Exception as e:
        print(f"✗ 9 elements test failed with unexpected error: {e}")

def test_lattice_auto_convert():
    """Test Issue #4: Auto-convert lattice inputs to strings"""
    print("\n=== Testing Lattice Auto-Conversion ===")
    
    # Test with integer inputs (should be converted to strings)
    integer_lattice = [
        [8, 4, 8],
        [6, 'w', 6],  # Mix of int and string
        [4, 8, 4],
    ]
    
    try:
        lattice = TestLattice(lattice_str=integer_lattice)
        print("✓ Integer lattice conversion implemented successfully")
        
        # Verify the conversion worked by checking source bounds are set
        if (lattice.source_lower_left != [0, 0, 0] and 
            lattice.source_upper_right != [0, 0, 0]):
            print("✓ Lattice built successfully with integer inputs converted to strings")
        else:
            print("✗ Lattice built but source bounds not set properly")
            
    except Exception as e:
        print(f"✗ Integer lattice conversion failed: {e}")

def test_source_region():
    """Test Issue #3: Source region implementation"""
    print("\n=== Testing Source Region ===")
    
    try:
        lattice = TestLattice()
        print(f"✓ Source lower left: {lattice.source_lower_left}")
        print(f"✓ Source upper right: {lattice.source_upper_right}")
        
        # Check if source region makes sense
        if (lattice.source_lower_left != [0, 0, 0] and 
            lattice.source_upper_right != [0, 0, 0]):
            print("✓ Source region bounds are defined")
        else:
            print("✗ Source region bounds not properly set")
            
    except Exception as e:
        print(f"✗ Source region test failed: {e}")

def test_settings_creation():
    """Test settings.xml creation"""
    print("\n=== Testing Settings Creation ===")
    
    try:
        settings = SettingsOpenMC()
        print(f"✓ Settings object created with XS lib: {settings.xs_lib}")
        print(f"✓ Cross sections path: {settings.xs_xml}")
        
        # Check if sources parameter exists
        if hasattr(settings, 'sources'):
            print(f"✓ Sources parameter exists: {settings.sources}")
        else:
            print("✗ Sources parameter missing")
        
        # Test source creation
        try:
            lattice = TestLattice()
            source = settings.create_source(
                lattice.source_lower_left, 
                lattice.source_upper_right, 
                'uniform'
            )
            print("✓ Source created successfully for lattice region")
            print(f"✓ Number of sources defined: {len(settings.sources)}")
        except Exception as e:
            print(f"✗ Source creation failed: {e}")
        
        # Test settings.xml creation
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                settings_file = settings.create_settings_xml(output_path=temp_dir)
                if os.path.exists(settings_file):
                    print("✓ settings.xml file created successfully")
                else:
                    print("✗ settings.xml file not found")
        except Exception as e:
            print(f"✗ settings.xml creation failed: {e}")
            
    except Exception as e:
        print(f"✗ Settings creation failed: {e}")

def test_absorption_rod():
    """Test Issue #6: Absorption rod implementation"""
    print("\n=== Testing Absorption Rod ===")
    
    try:
        from vr1.lattice_units import IRT4M, AbsRod
        
        # Test IRT4M with absorption rod
        irt4m_abs = IRT4M(materials=vr1_materials, fa_type='6', abs_rod_height=10.0)
        print("✓ IRT4M with abs_rod_height created")
        
        # Try to build it (this might fail due to surface issues)
        try:
            universe = irt4m_abs.build()
            print("✓ IRT4M with absorption rod built successfully")
        except Exception as e:
            print(f"✗ IRT4M with absorption rod build failed: {e}")
        
        # Test AbsRod directly
        try:
            abs_rod = AbsRod(materials=vr1_materials, rod_height=10.0)
            abs_universe = abs_rod.build()
            print("✓ AbsRod built successfully")
        except Exception as e:
            print(f"✗ AbsRod build failed: {e}")
            
    except Exception as e:
        print(f"✗ Absorption rod import/creation failed: {e}")

if __name__ == "__main__":
    print("Testing VR1 OpenMC Issues")
    print("=" * 50)
    
    test_lattice_reformatter()
    test_lattice_auto_convert() 
    test_source_region()
    test_settings_creation()
    test_absorption_rod()
    
    print("\n" + "=" * 50)
    print("Testing complete")