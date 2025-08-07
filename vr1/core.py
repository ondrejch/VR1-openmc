""" Core design for VR1 """
import openmc
from vr1.materials import VR1Materials, vr1_materials
from vr1.lattice_units import (rects, plane_zs, lattice_unit_names, lattice_lower_left, lattice_upper_right,
                               IRT4M, lattice_pitch, LatticeUnitVR1)

# Write an FA lattice, or the core lattice, or the whole reactor
core_types: list[str] = ['fuel_lattice', 'active_zone', 'reactor']

# Different core designs.
core_designs: dict[str, list[list[str]]] = {
    'small_test':  [
        ['8', '4', '8'],
        ['6', 'w', '6'],
        ['4', '8', '4'],
    ]
}

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
    def __init__(self,materials : VR1Materials = vr1_materials):
        self.materials = materials
        self.source_lower_left:  list[float] = [0, 0, 0]  # Boundaries for source
        self.source_upper_right: list[float] = [0, 0, 0]
        self.model = openmc.Universe


class FuelAssembly(VR1core):
    """ Returns a fuel assembly """
    def __init__(self, fa_type, materials: VR1Materials = vr1_materials, boundaries='reflective'):
        super().__init__(materials)
        if fa_type not in list(lattice_unit_names.keys()):
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type = fa_type
        self.model = IRT4M(self.fa_type, boundaries)
        self.source_lower_left = lattice_lower_left
        self.source_upper_right = lattice_upper_right


class TestLattice(VR1core):
    def reformat(self, lattice_str):
        """
        Reformats lattice string to be an 8x8 grid
        Upper-left justified
        """
        new_lattice_str = []
        for row in lattice_str:
            if len(row) == 8:
                new_lattice_str.append(row)
                n -= 1
                continue
            elif len(row) > 8:
                raise ValueError('All lattice rows must be of length 8 or shorter')
            n = 8 - len(row)
            while n > 0:
                if n % 2 == 0:
                    row = ['w'] + row
                else:
                    row = row + ['w']
                n -= 1
            new_lattice_str.append(row)
        if len(new_lattice_str) < 8:
            n = 8 - len(new_lattice_str)
            while n > 0:
                if n%2 == 0:
                    new_lattice_str = [['w','w','w','w','w','w','w','w']] + new_lattice_str
                else:
                    new_lattice_str = new_lattice_str + [['w','w','w','w','w','w','w','w']]
                n -= 1
        if len(new_lattice_str) != 8:
            raise ValueError('Reformatting failed unexpectedly')
        for i in range(2, 6):
            new_lattice_str[-1][i] = 'wrc'
        return new_lattice_str

    def __init__(self, materials : VR1Materials = vr1_materials, lattice_str: list[list[str]] = None):
        super().__init__(materials)
        lattice_str = self.reformat(lattice_str)
        if lattice_str is None:
            lattice_str = core_designs['small_test']
        n: int = len(lattice_str)
        assert n > 0
        # for row in lattice_str:
        #     if len(row) != n:
        #         raise ValueError(f'{lattice_str} is not square')
        self.lattice = openmc.RectLattice(name='test_lattice')
        xy_corner: float = float(n) * lattice_pitch / 2.0
        self.lattice.lower_left = (-xy_corner, -xy_corner)
        self.lattice.pitch = (lattice_pitch, lattice_pitch)
        # self.lattice.universes = np.zeros((n, n), dtype=openmc.UniverseBase)  # TODO why is this not working?
        lattice_builder = LatticeUnitVR1(self.materials)
        lattice_builder.load()
        lattice_array: list[list[openmc.UniverseBase]] = []  # TODO Is there a better way?
        z: int = 0
        for i in range(n):
            _l: list[openmc.UniverseBase] = []
            for j in range(n):
                _l.append(lattice_builder.get(lattice_str[i][j]))
            lattice_array.append(_l)

            z += 1
        self.lattice.universes = lattice_array
        """ Lattice box """
        z0: float = plane_zs['H01.sc']
        z1: float = plane_zs['FAZ.2']
        lattice_box = openmc.model.RectangularParallelepiped(-xy_corner, xy_corner, -xy_corner, xy_corner, z0, z1)
        lattice_cell = openmc.Cell(fill=self.lattice, region=-lattice_box)
        self.model = openmc.Universe(cells=[lattice_cell])
        # TODO: Create an AmBe fixed starter source definition
        self.source_lower_left = (-xy_corner, -xy_corner, lattice_lower_left[2])
        self.source_upper_right = (xy_corner, xy_corner, lattice_upper_right[2])
