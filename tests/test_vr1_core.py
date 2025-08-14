"""
Comprehensive unit tests for VR1 OpenMC core functionality

This test suite validates all implemented features:
- Lattice reformatter with 8+ elements support
- Integer to string auto-conversion
- Source region definition
- Settings.xml creation
- Absorption rod implementation
"""

import pytest
import tempfile
import os
import sys

# Add vr1 to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vr1.core import TestLattice, FuelAssembly, core_designs
from vr1.settings import SettingsOpenMC
from vr1.materials import vr1_materials
from vr1.lattice_units import IRT4M, AbsRod


class TestLatticeReformatter:
    """Test lattice reformatter functionality (Issue #1)"""
    
    def test_reformat_8_elements(self):
        """Test that 8-element rows are handled correctly"""
        lattice = TestLattice()
        input_8 = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]
        result = lattice.reformat(input_8)
        
        assert len(result) == 8, "Should pad to 8 rows"
        assert len(result[0]) == 8, "First row should have 8 elements"
        assert result[0] == ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'], "8-element row should be preserved"
    
    def test_reformat_more_than_8_elements(self):
        """Test that rows with >8 elements raise ValueError"""
        lattice = TestLattice()
        input_9 = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
        
        with pytest.raises(ValueError, match="All lattice rows must be of length 8 or shorter"):
            lattice.reformat(input_9)
    
    def test_reformat_smaller_configuration(self):
        """Test reformatting of smaller configurations"""
        lattice = TestLattice()
        small_config = [['8', '4'], ['6', 'w']]
        result = lattice.reformat(small_config)
        
        assert len(result) == 8, "Should pad to 8 rows"
        assert all(len(row) == 8 for row in result), "All rows should have 8 elements"
        assert result[-1][2:6] == ['wrc', 'wrc', 'wrc', 'wrc'], "Should add water reflector cells"
    
    def test_reformat_padding_logic(self):
        """Test that padding is applied correctly (upper-left justified)"""
        lattice = TestLattice()
        input_3 = [['a', 'b', 'c']]
        result = lattice.reformat(input_3)
        
        # Should pad 5 elements: alternating left/right starting with left for even n
        expected_first_row_elements = ['a', 'b', 'c']
        first_row = result[0]
        
        # Check that original elements are preserved and water cells added
        assert len(first_row) == 8
        assert all(elem in expected_first_row_elements or elem == 'w' for elem in first_row)


class TestAutoConversion:
    """Test integer to string auto-conversion (Issue #4)"""
    
    def test_integer_conversion(self):
        """Test that integers are converted to strings"""
        lattice = TestLattice()
        integer_config = [[8, 4, 8], [6, 'w', 6]]
        result = lattice.reformat(integer_config)
        
        # Check that all elements are strings
        for row in result:
            for element in row:
                assert isinstance(element, str), f"Element {element} should be string"
    
    def test_mixed_integer_string_input(self):
        """Test mixed integer and string inputs"""
        config = [[8, 4, 8], [6, 'w', 6], [4, 8, 4]]
        lattice = TestLattice(lattice_str=config)
        
        # Should build successfully without errors
        assert lattice.source_lower_left != [0, 0, 0]
        assert lattice.source_upper_right != [0, 0, 0]
    
    def test_pure_integer_lattice(self):
        """Test lattice with all integer inputs"""
        integer_lattice = [[8, 4, 8], [6, 8, 6], [4, 8, 4]]
        lattice = TestLattice(lattice_str=integer_lattice)
        
        # Should build successfully
        assert hasattr(lattice, 'lattice')
        assert hasattr(lattice, 'model')


class TestSourceRegion:
    """Test source region implementation (Issue #3)"""
    
    def test_source_region_bounds(self):
        """Test that source region bounds are properly set"""
        lattice = TestLattice()
        
        assert lattice.source_lower_left != [0, 0, 0], "Source lower left should be set"
        assert lattice.source_upper_right != [0, 0, 0], "Source upper right should be set"
        
        # Check bounds are reasonable (negative to positive)
        assert lattice.source_lower_left[0] < lattice.source_upper_right[0], "X bounds should be ordered"
        assert lattice.source_lower_left[1] < lattice.source_upper_right[1], "Y bounds should be ordered"
        assert lattice.source_lower_left[2] < lattice.source_upper_right[2], "Z bounds should be ordered"
    
    def test_fuel_assembly_source_region(self):
        """Test fuel assembly source region"""
        fa = FuelAssembly('8')
        
        assert fa.source_lower_left != [0, 0, 0]
        assert fa.source_upper_right != [0, 0, 0]


class TestSettingsCreation:
    """Test settings.xml creation and source definition (Issue #3)"""
    
    def test_settings_object_creation(self):
        """Test basic settings object creation"""
        settings = SettingsOpenMC()
        
        assert hasattr(settings, 'xs_lib')
        assert hasattr(settings, 'sources')
        assert settings.sources is None  # Initially no sources
    
    def test_source_creation(self):
        """Test source creation for lattice"""
        settings = SettingsOpenMC()
        lattice = TestLattice()
        
        source = settings.create_source(
            lattice.source_lower_left,
            lattice.source_upper_right,
            'uniform'
        )
        
        assert source is not None
        assert len(settings.sources) == 1
        assert hasattr(source, 'space')
        assert hasattr(source, 'angle')
        assert hasattr(source, 'energy')
    
    def test_point_source_creation(self):
        """Test point source creation"""
        settings = SettingsOpenMC()
        lattice = TestLattice()
        
        source = settings.create_source(
            lattice.source_lower_left,
            lattice.source_upper_right,
            'point'
        )
        
        assert source is not None
        assert len(settings.sources) == 1
    
    def test_settings_xml_creation(self):
        """Test settings.xml file creation"""
        settings = SettingsOpenMC()
        lattice = TestLattice()
        
        # Create source first
        settings.create_source(
            lattice.source_lower_left,
            lattice.source_upper_right,
            'uniform'
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = settings.create_settings_xml(output_path=temp_dir)
            
            assert os.path.exists(settings_file), "Settings file should be created"
            assert settings_file.endswith('settings.xml'), "Should create settings.xml"


class TestAbsorptionRod:
    """Test absorption rod implementation (Issue #6)"""
    
    def test_irt4m_with_absorption_rod(self):
        """Test IRT4M with absorption rod height"""
        irt4m_abs = IRT4M(materials=vr1_materials, fa_type='6', abs_rod_height=10.0)
        
        assert irt4m_abs.abs_rod_height == 10.0
        
        # Should build without errors
        universe = irt4m_abs.build()
        assert universe is not None
    
    def test_absorption_rod_direct(self):
        """Test AbsRod class directly"""
        abs_rod = AbsRod(materials=vr1_materials, rod_height=15.0)
        
        assert abs_rod.rod_height == 15.0
        assert abs_rod.name() == 'Cadmium absorption rod'
        
        # Should build without errors
        universe = abs_rod.build()
        assert universe is not None
    
    def test_lattice_unit_absorption_rod(self):
        """Test lattice unit with absorption rod codes"""
        from vr1.lattice_units import LatticeUnitVR1
        
        lattice_builder = LatticeUnitVR1(vr1_materials)
        lattice_builder.load()
        
        # Test 'O' (fully withdrawn) and 'X' (fully inserted) control rods
        universe_o = lattice_builder.get('O')
        universe_x = lattice_builder.get('X')
        
        assert universe_o is not None
        assert universe_x is not None
    
    def test_variable_absorption_rod_height(self):
        """Test variable absorption rod height with AR prefix"""
        from vr1.lattice_units import LatticeUnitVR1
        
        lattice_builder = LatticeUnitVR1(vr1_materials)
        lattice_builder.load()
        
        # Test AR code with specific height
        universe_ar = lattice_builder.get('AR25.5')  # 25.5 cm insertion
        assert universe_ar is not None


class TestFuelAssembly:
    """Test fuel assembly functionality"""
    
    def test_valid_fuel_assembly_types(self):
        """Test creation of valid fuel assembly types"""
        for fa_type in ['4', '6', '8']:
            fa = FuelAssembly(fa_type)
            assert fa.fa_type == fa_type
            assert hasattr(fa, 'model')
    
    def test_invalid_fuel_assembly_type(self):
        """Test that invalid FA types raise ValueError"""
        with pytest.raises(ValueError, match="is not a known lattice unit type"):
            FuelAssembly('invalid_type')
    
    def test_non_fuel_assembly_type(self):
        """Test that non-FA types raise ValueError"""
        with pytest.raises(ValueError, match="is not a known fuel assembly type"):
            FuelAssembly('w')  # Water cell, not a fuel assembly


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_lattice_workflow(self):
        """Test complete workflow from lattice creation to simulation setup"""
        # Create lattice with mixed inputs
        config = [[8, 4, 8], [6, 'w', 6], [4, 8, 4]]
        lattice = TestLattice(lattice_str=config)
        
        # Create settings and source
        settings = SettingsOpenMC()
        source = settings.create_source(
            lattice.source_lower_left,
            lattice.source_upper_right,
            'uniform'
        )
        
        # Create settings file
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = settings.create_settings_xml(output_path=temp_dir)
            assert os.path.exists(settings_file)
        
        # Verify all components exist
        assert lattice.model is not None
        assert source is not None
        assert len(settings.sources) == 1
    
    def test_absorption_rod_lattice_workflow(self):
        """Test workflow with absorption rods in lattice"""
        # Create lattice with control rods
        config = [['8', 'O', '8'], ['X', 'w', 'AR10.5']]  # Mix of rod types
        lattice = TestLattice(lattice_str=config)
        
        # Should build successfully
        assert lattice.model is not None
        assert lattice.source_lower_left != [0, 0, 0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])