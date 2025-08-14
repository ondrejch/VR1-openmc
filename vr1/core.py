"""
VR1 OpenMC Core Design Module

This module provides classes for building VR1 reactor core geometries with OpenMC.
It includes functionality for fuel assemblies, lattice configurations, and source regions.

Classes:
    VR1core: Base class for VR1 reactor components
    FuelAssembly: Individual fuel assembly geometry 
    TestLattice: Configurable lattice geometry with automatic formatting

Features:
    - Automatic lattice reformatting to 8x8 grid
    - Integer to string auto-conversion for lattice inputs
    - Source region definition for arbitrary lattice configurations
    - Support for absorption rod configurations
"""

import openmc
from vr1.materials import VR1Materials, vr1_materials
from vr1.lattice_units import (rects, plane_zs, lattice_unit_names, lattice_lower_left, lattice_upper_right,
                               IRT4M, lattice_pitch, LatticeUnitVR1)

# Core geometry types available for simulation
core_types: list[str] = ['fuel_lattice', 'active_zone', 'reactor']

# Predefined core designs for testing and validation
core_designs: dict[str, list[list[str]]] = {
    'small_test':  [
        ['8', '4', '8'],  # 8-tube FA, 4-tube FA, 8-tube FA
        ['6', 'w', '6'],  # 6-tube FA, water, 6-tube FA
        ['4', '8', '4'],  # 4-tube FA, 8-tube FA, 4-tube FA
    ]
}

# Template for empty 8x8 lattice configuration
# Row/column labels with water cells, useful for GUI development
VR1_EMPTY_LATTICE_TEMPLATE: list[list[str]] = [
    ['0', '1', '2', '3', '4', '5', '6', '7'],  # Column labels
    ['1', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 1: water cells
    ['2', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 2: water cells
    ['3', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 3: water cells
    ['4', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 4: water cells
    ['5', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 5: water cells
    ['6', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 6: water cells
    ['7', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Row 7: water cells
]


class VR1core:
    """
    Base class for VR1 reactor components
    
    This class provides the fundamental structure for VR1 reactor geometry components,
    including material definitions and source region boundaries. All VR1 reactor 
    components inherit from this class.
    
    Attributes:
        materials (VR1Materials): Material definitions for the reactor
        source_lower_left (list[float]): Lower left corner of source region [x, y, z]
        source_upper_right (list[float]): Upper right corner of source region [x, y, z]
        model (openmc.Universe): OpenMC universe model
    
    Args:
        materials (VR1Materials, optional): Material definitions. Defaults to vr1_materials.
    """
    def __init__(self, materials: VR1Materials = vr1_materials):
        self.materials = materials
        # Initialize source region boundaries (to be set by derived classes)
        self.source_lower_left: list[float] = [0, 0, 0]
        self.source_upper_right: list[float] = [0, 0, 0]
        self.model = openmc.Universe


class FuelAssembly(VR1core):
    """
    Individual fuel assembly geometry for VR1 reactor
    
    This class creates a single fuel assembly with the specified type and boundary
    conditions. It validates the fuel assembly type and sets up the appropriate
    source region boundaries.
    
    Attributes:
        fa_type (str): Type of fuel assembly ('4', '6', '8' for number of tubes)
        model (IRT4M): OpenMC fuel assembly model
    
    Args:
        fa_type (str): Fuel assembly type identifier
        materials (VR1Materials, optional): Material definitions. Defaults to vr1_materials.
        boundaries (str, optional): Boundary conditions. Defaults to 'reflective'.
    
    Raises:
        ValueError: If fa_type is not a known lattice unit type or fuel assembly type
        
    Example:
        >>> fa = FuelAssembly('8', boundaries='reflective')  # 8-tube fuel assembly
        >>> print(fa.fa_type)  # '8'
    """
    def __init__(self, fa_type: str, materials: VR1Materials = vr1_materials, boundaries: str = 'reflective'):
        super().__init__(materials)
        
        # Validate fuel assembly type
        if fa_type not in list(lattice_unit_names.keys()):
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
            
        self.fa_type = fa_type
        self.model = IRT4M(materials=self.materials, fa_type=self.fa_type, boundary=boundaries)
        
        # Set source region to fuel assembly active region
        self.source_lower_left = lattice_lower_left
        self.source_upper_right = lattice_upper_right


class TestLattice(VR1core):
    """
    Configurable lattice geometry with automatic formatting for VR1 reactor
    
    This class creates a reactor core lattice with automatic reformatting to 8x8 grid,
    integer to string conversion, and proper source region definition. It supports
    arbitrary lattice configurations and automatically pads/centers smaller configurations.
    
    Key Features:
        - Automatic reformatting to 8x8 grid (upper-left justified)
        - Integer to string auto-conversion for user convenience
        - Source region calculation based on lattice geometry
        - Support for control rod configurations (absorption rod heights)
        - Water reflector cells automatically added at bottom
    
    Attributes:
        lattice (openmc.RectLattice): OpenMC rectangular lattice
        model (openmc.Universe): Complete lattice universe with bounding box
    
    Args:
        materials (VR1Materials, optional): Material definitions. Defaults to vr1_materials.
        lattice_str (list[list[str]], optional): Lattice configuration. Defaults to 'small_test'.
    
    Example:
        >>> # Create lattice with mixed integer/string inputs
        >>> config = [[8, 4, 8], [6, 'w', 6], [4, 8, 4]]
        >>> lattice = TestLattice(lattice_str=config)
        >>> print(lattice.source_lower_left)  # Source region bounds
    """
    
    def reformat(self, lattice_str: list[list]) -> list[list[str]]:
        """
        Reformats lattice configuration to standard 8x8 grid format
        
        This method performs several key transformations:
        1. Auto-converts integers to strings for lattice codes
        2. Pads rows shorter than 8 elements with water cells ('w')
        3. Centers configurations smaller than 8x8 by padding with water rows
        4. Adds water reflector cells ('wrc') at bottom center positions
        
        Args:
            lattice_str (list[list]): Input lattice configuration of any size
        
        Returns:
            list[list[str]]: Standardized 8x8 lattice with string codes
            
        Raises:
            ValueError: If any row has more than 8 elements
            ValueError: If reformatting logic fails unexpectedly
            
        Example:
            >>> lattice = TestLattice()
            >>> small_config = [[8, 4], [6, 'w']]
            >>> formatted = lattice.reformat(small_config)
            >>> len(formatted)  # 8 (rows)
            >>> len(formatted[0])  # 8 (columns)
        """
        # Step 1: Auto-convert integers to strings for user convenience
        converted_lattice = []
        for row in lattice_str:
            converted_row = []
            for element in row:
                if isinstance(element, int):
                    converted_row.append(str(element))
                else:
                    converted_row.append(element)
            converted_lattice.append(converted_row)
        
        # Step 2: Pad rows to 8 elements (upper-left justified)
        new_lattice_str = []
        for row in converted_lattice:
            if len(row) == 8:
                new_lattice_str.append(row)
                continue
            elif len(row) > 8:
                raise ValueError('All lattice rows must be of length 8 or shorter')
            
            # Pad rows shorter than 8 elements with water cells
            n = 8 - len(row)
            padded_row = row[:]  # Copy to avoid modifying original
            while n > 0:
                if n % 2 == 0:
                    padded_row = ['w'] + padded_row  # Pad left
                else:
                    padded_row = padded_row + ['w']  # Pad right
                n -= 1
            new_lattice_str.append(padded_row)
        
        # Step 3: Pad lattice to 8 rows (center vertically)
        if len(new_lattice_str) < 8:
            n = 8 - len(new_lattice_str)
            water_row = ['w'] * 8
            while n > 0:
                if n % 2 == 0:
                    new_lattice_str = [water_row[:]] + new_lattice_str  # Add top
                else:
                    new_lattice_str = new_lattice_str + [water_row[:]]  # Add bottom
                n -= 1
        
        # Validation check
        if len(new_lattice_str) != 8:
            raise ValueError('Reformatting failed unexpectedly')
        
        # Step 4: Add water reflector cells at bottom center (positions 2-5)
        for i in range(2, 6):
            new_lattice_str[-1][i] = 'wrc'
            
        return new_lattice_str

    def __init__(self, materials: VR1Materials = vr1_materials, lattice_str: list[list] = None):
        """
        Initialize TestLattice with automatic formatting and geometry construction
        
        This constructor performs the complete lattice setup:
        1. Format input lattice to 8x8 standard
        2. Calculate geometry bounds
        3. Build OpenMC lattice with appropriate universe fills
        4. Create bounding geometry box
        5. Set source region boundaries
        
        Args:
            materials (VR1Materials, optional): Material definitions
            lattice_str (list[list], optional): Lattice configuration (any size)
        """
        super().__init__(materials)
        
        # Use default design if no lattice specified
        if lattice_str is None:
            lattice_str = core_designs['small_test']
        
        # Format to standard 8x8 configuration
        lattice_str = self.reformat(lattice_str)
        n: int = len(lattice_str)
        assert n == 8, f"Reformatted lattice should be 8x8, got {n}x{len(lattice_str[0])}"
        
        # Create OpenMC rectangular lattice
        self.lattice = openmc.RectLattice(name='vr1_test_lattice')
        xy_corner: float = float(n) * lattice_pitch / 2.0
        self.lattice.lower_left = (-xy_corner, -xy_corner)
        self.lattice.pitch = (lattice_pitch, lattice_pitch)
        
        # Build lattice universe array
        lattice_builder = LatticeUnitVR1(self.materials)
        lattice_builder.load()  # Load all available lattice unit types
        
        # Create 2D array of universes corresponding to lattice configuration
        lattice_array: list[list[openmc.Universe]] = []
        for i in range(n):
            row_universes: list[openmc.Universe] = []
            for j in range(n):
                # Get universe for each lattice position
                universe = lattice_builder.get(lattice_str[i][j])
                row_universes.append(universe)
            lattice_array.append(row_universes)
        
        self.lattice.universes = lattice_array
        
        # Create bounding geometry box (from small channel bottom to fuel assembly top)
        z0: float = plane_zs['H01.sc']  # Bottom boundary (small channel insertion)
        z1: float = plane_zs['FAZ.2']   # Top boundary (fuel assembly top)
        lattice_box = openmc.model.RectangularParallelepiped(
            -xy_corner, xy_corner,  # x bounds
            -xy_corner, xy_corner,  # y bounds 
            z0, z1                  # z bounds
        )
        
        # Create lattice cell and universe
        lattice_cell = openmc.Cell(fill=self.lattice, region=-lattice_box)
        self.model = openmc.Universe(cells=[lattice_cell])
        
        # Set source region boundaries for neutron source definition
        # Source region covers the entire lattice active fuel region
        self.source_lower_left = (-xy_corner, -xy_corner, lattice_lower_left[2])
        self.source_upper_right = (xy_corner, xy_corner, lattice_upper_right[2])
