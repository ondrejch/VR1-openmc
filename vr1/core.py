""" Core design for VR1 """
import openmc
from vr1.materials import vr1_materials
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
    def __init__(self):
        self.materials = vr1_materials
        self.source_lower_left:  list[float] = [0, 0, 0]  # Boundaries for source
        self.source_upper_right: list[float] = [0, 0, 0]
        self.model = openmc.Universe


class FuelAssembly(VR1core):
    """ Returns a fuel assembly """
    def __init__(self, fa_type, boundaries='reflective'):
        super().__init__()
        if fa_type not in list(lattice_unit_names.keys()):
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type = fa_type
        self.model = IRT4M(self.fa_type, boundaries)
        self.source_lower_left = lattice_lower_left
        self.source_upper_right = lattice_upper_right


class TestLattice(VR1core):
    def __init__(self, lattice_str: (None, list[list[str]]) = None):
        super().__init__()
        if lattice_str is None:
            lattice_str = core_designs['small_test']
        n: int = len(lattice_str)
        print(f'Lattice size {n}')
        assert n > 0
        for row in lattice_str:
            if len(row) != n:
                raise ValueError(f'{lattice_str} is not square')
        self.lattice = openmc.RectLattice(name='test_lattice')
        xy_corner: float = float(n) * lattice_pitch / 2.0
        self.lattice.lower_left = (-xy_corner, -xy_corner)
        self.lattice.pitch = (lattice_pitch, lattice_pitch)
        # self.lattice.universes = np.zeros((n, n), dtype=openmc.UniverseBase)  # TODO why is this not working?
        lattice_builder = LatticeUnitVR1()
        lattice_array: list[list[openmc.UniverseBase]] = []  # TODO Is there a better way?
        for i in range(n):
            _l: list[openmc.UniverseBase] = []
            for j in range(n):
                _l.append(lattice_builder.get(lattice_str[i][j]))
            lattice_array.append(_l)
        self.lattice.universes = lattice_array
        """ Lattice box """
        z0: float = plane_zs['FAZ.5']
        z1: float = plane_zs['FAZ.2']
        lattice_box = openmc.model.RectangularParallelepiped(-xy_corner, xy_corner, -xy_corner, xy_corner, z0, z1)
        lattice_cell = openmc.Cell(fill=self.lattice, region=-lattice_box)
        """ Water box around the lattice """
        x0: float = rects['CORE.rec'][0]
        x1: float = rects['CORE.rec'][1]
        y0: float = rects['CORE.rec'][2]
        y1: float = rects['CORE.rec'][3]
        z0: float = plane_zs['FAZ.6']
        z1: float = plane_zs['FAZ.1']
        core_box = openmc.model.RectangularParallelepiped(x0, x1, y0, y1, z0, z1)
        core_box.boundary_type = 'vacuum'
        core_cell = openmc.Cell(fill=self.materials.water, region=-core_box & +lattice_box)
        self.model = openmc.Universe(cells=[lattice_cell, core_cell])
        self.source_lower_left = (-xy_corner, -xy_corner, lattice_lower_left[2])
        self.source_upper_right = (xy_corner, xy_corner, lattice_upper_right[2])
