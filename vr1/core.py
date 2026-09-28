""" Core design for VR1 """

from __future__ import annotations

import warnings

import openmc
from vr1.materials import VR1Materials, vr1_materials
from vr1.lattice_units import (
    IRT4M,
    AbsRod,
    LatticeUnitVR1,
    lattice_lower_left,
    lattice_pitch,
    lattice_unit_names,
    lattice_upper_right,
    plane_zs,
)

# Write an FA lattice, or the core lattice, or the whole reactor
core_types: list[str] = ['fuel_lattice', 'active_zone', 'reactor']

# Different core designs.
core_designs: dict[str, list[list[str]]] = {
    'small_test':  [
        ['8', '4', '8'],
        ['6', 'w', '6'],
        ['4', '8', '4'],
    ],
    'C12-C-2023': 
    [['w','w','w','w','w','w','w','w'],
    ['v56','d','d','8','8','d','d','v56'],
    ['w','d','v12_6','X','6','X','d','w'],
    ['w','8','X','rt','X','8','8','w'],
    ['w','8','6','X','v56','8','8','w'],
    ['v56','d','d','X','6','d','d','v56'],
    ['w','w','w','w','w','w','w','w'],
    ['v56','w','w','v56','w','w','w','w']]
}

# Fuel assembly codes with a control rod: (assembly type, rod height [cm]),
# as built by LatticeUnitVR1
rodded_fa_types: dict[str, tuple[str, float]] = {
    'X': ('6', 0.0),
    'O': ('6', 84.7),
    'X4': ('4', 0.0),
    'O4': ('4', 84.7),
}

# Bottom-row columns under the radial channel, which have no grid plate
radial_channel_columns: range = range(2, 6)

VR1_EMPTY_LATTICE_TEMPLATE: list[list[str]] = [
    ['0', '1', '2', '3', '4', '5', '6', '7'],
    ['1', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['2', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['3', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['4', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['5', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['6', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ['7', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
]


class VR1core:
    """ TODO: lattice structure, geometry of the overall reactor, pool, channels """

    def __init__(self, materials: VR1Materials = vr1_materials):
        """Initialize shared core-level state."""
        self.materials = materials
        # self.source_lower_left:  list[float] = [-20, -20, 5]  # Boundaries for source if bottom definition doesn't work
        # self.source_upper_right: list[float] = [20, 20, 70]
        self.source_lower_left:  list[float] = [0, 0, 40]  # Boundaries for source
        self.source_upper_right: list[float] = [0, 0, 40]
        self.model = openmc.Universe


class FuelAssembly(VR1core):
    """ Returns a fuel assembly """

    def __init__(self, fa_type, materials: VR1Materials = vr1_materials, boundaries='reflective'):
        """Initialize a new instance of a fuel assembly model with specified parameters.
        Parameters:
            - fa_type (str): The type of fuel assembly: a fuel assembly lattice unit type,
              or a rodded one from ``rodded_fa_types`` ('X', 'O', 'X4', 'O4').
            - materials (VR1Materials): The materials used in the fuel assembly, defaults to vr1_materials.
            - boundaries (str): The type of boundary condition, defaults to 'reflective'.
        Returns:
            - None"""
        super().__init__(materials)
        if fa_type not in rodded_fa_types:
            if fa_type not in lattice_unit_names:
                raise ValueError(f'{fa_type} is not a known lattice unit type!')
            if 'FA' not in lattice_unit_names[fa_type]:
                raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type = fa_type
        if fa_type in rodded_fa_types:
            assembly_type, rod_height = rodded_fa_types[fa_type]
            self.model = AbsRod(
                materials=self.materials,
                assembly_type=assembly_type,
                rod_height=rod_height,
                boundary=boundaries,
            ).build()
        else:
            self.model = IRT4M(
                materials=self.materials,
                fa_type=self.fa_type,
                boundary=boundaries,
            ).build()
        self.source_lower_left = lattice_lower_left
        self.source_upper_right = lattice_upper_right


class Lattice(VR1core):
    """
    Represents a lattice-based geometry for simulations, supporting custom or preset material configurations.
    Parameters:
        - materials (VR1Materials): The materials to be used within the lattice structure.
        - lattice_str (list[list[str]], optional): A 2D list representing the layout of the lattice. Defaults to None.
        - preset (bool, optional): If True and lattice_str is None, uses a preset lattice configuration. Defaults to False.
    Processing Logic:
        - The lattice string is reformatted to ensure it forms an 8x8 grid, adding 'w' as necessary.
        - The class raises a ValueError if given lattice rows exceed length 8 or the lattice string is not provided without a preset.
        - A lattice box defines the boundaries of the simulation using given planar coordinates.
    """
    def reformat(self, lattice_str: list[list[str]]) -> list[list[str]]:
        """
        Reformats lattice string to be an 8x8 grid
        Upper-left justified
        """
        new_lattice_str = []
        for row in lattice_str:
            row = list(row)
            n = 8 - len(row)
            if len(row) == 8:
                new_lattice_str.append(row)
                continue
            if len(row) > 8:
                raise ValueError('All lattice rows must be of length 8 or shorter')
            while n > 0:
                if n % 2 == 0:
                    row = ['w'] + row
                else:
                    row += ['w']
                n -= 1
            new_lattice_str.append(row)
        if len(new_lattice_str) < 8:
            n = 8 - len(new_lattice_str)
            while n > 0:
                if n%2 == 0:
                    new_lattice_str = [['w','w','w','w','w','w','w','w']] + new_lattice_str
                else:
                    new_lattice_str += [['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w']]
                n -= 1
        if len(new_lattice_str) != 8:
            raise ValueError('Reformatting failed unexpectedly')
        replaced = []
        for i in radial_channel_columns:
            if new_lattice_str[-1][i] not in ('w', 'wrc'):
                replaced.append(f'[7][{i}]={new_lattice_str[-1][i]!r}')
            new_lattice_str[-1][i] = 'wrc'
        if replaced:
            warnings.warn(
                'Lattice positions under the radial channel were replaced by water (wrc): '
                + ', '.join(replaced),
                stacklevel=3,
            )
        return new_lattice_str

    def __init__(
        self,
        materials: VR1Materials = vr1_materials,
        lattice_str: list[list[str]] | None = None,
        preset: str | list[list[str]] | None = None,
        lattice_file : str | None = None
    ):
        """Initializes an instance of a lattice-based geometry with specified or preset configurations.
        Parameters:
            - materials (VR1Materials): The materials to be used within the lattice structure.
            - lattice_str (list[list[str]], optional): A 2D list representing the layout of the lattice. Defaults to None.
            - preset (str | list[list[str]] | None, optional): Preset name or lattice
              definition used when ``lattice_str`` is not provided.
        Returns:
            - None: This is a constructor method; it initializes the instance and does not return a value."""
        super().__init__(materials)
        if lattice_str is None:
            if preset is None:
                raise ValueError('Must specify lattice string or provide a preset lattice')
            if isinstance(preset, str):
                if preset not in core_designs:
                    raise ValueError(
                        f'Unknown preset "{preset}". '
                        f"Available presets: {sorted(core_designs.keys())}"
                    )
                lattice_str = core_designs[preset]
            elif isinstance(preset, list):
                lattice_str = preset
            else:
                raise TypeError('Preset must be a preset name or a lattice list')
        self.lattice_str = [[str(i) for i in j] for j in lattice_str]
        self.lattice_str = self.reformat(self.lattice_str)
        self.build()

    def build(self):
        """Build the OpenMC lattice universe from the current lattice string."""
        n = 8
        self.lattice = openmc.RectLattice(name='test_lattice')
        xy_corner: float = float(n) * lattice_pitch / 2.0
        self.lattice.lower_left = (-xy_corner, -xy_corner)
        self.lattice.pitch = (lattice_pitch, lattice_pitch)
        lattice_builder = LatticeUnitVR1(self.materials)
        lattice_builder.load()
        lattice_array: list[list[openmc.UniverseBase]] = []
        universe_cache: dict[str, openmc.UniverseBase] = {}
        for i in range(n):
            _l: list[openmc.UniverseBase] = []
            for j in range(n):
                lattice_code = self.lattice_str[i][j]
                if lattice_code not in universe_cache:
                    universe_cache[lattice_code] = lattice_builder.get(lattice_code)
                _l.append(universe_cache[lattice_code])
            lattice_array.append(_l)
        self.lattice.universes = lattice_array
        """ Lattice box """
        z0: float = plane_zs['H01.sc']
        z1: float = plane_zs['FAZ.2']
        lattice_box = openmc.model.RectangularParallelepiped(-xy_corner, xy_corner, -xy_corner, xy_corner, z0, z1,boundary_type='vacuum')
        lattice_cell = openmc.Cell(fill=self.lattice, region=-lattice_box)
        self.model = openmc.Universe(cells=[lattice_cell])
        # TODO: Create an AmBe fixed starter source definition
        self.source_lower_left = (-xy_corner, -xy_corner, lattice_lower_left[2])
        self.source_upper_right = (xy_corner, xy_corner, lattice_upper_right[2])

    @staticmethod
    def control_rod_assembly_type(lattice_code: str) -> str | None:
        """Return the FA type ('6' or '4') of a control-rod lattice code, or None."""
        if lattice_code in rodded_fa_types:
            return rodded_fa_types[lattice_code][0]
        fa_type, sep, _ = lattice_code.partition('_')  # '6_<height>' or '4_<height>'
        if sep and fa_type in ('6', '4'):
            return fa_type
        return None

    def _set_control_rods(self, codes: dict[str, str]) -> None:
        """Replace every control-rod location with codes[FA type]."""
        for i in range(8):
            for j in range(8):
                fa_type = self.control_rod_assembly_type(self.lattice_str[i][j])
                if fa_type is not None:
                    self.lattice_str[i][j] = codes[fa_type]
        self.build()

    def SCRAM(self):
        """Set all control-rod locations to inserted state."""
        self._set_control_rods({'6': 'X', '4': 'X4'})

    def unSCRAM(self):
        """Set all control-rod locations to withdrawn state."""
        self._set_control_rods({'6': 'O', '4': 'O4'})
