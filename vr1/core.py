""" Core design for VR1 """
import numpy as np
import openmc
from vr1.lattice_units import (surfaces, rects, plane_zs, lattice_unit_names, lattice_lower_left, lattice_upper_right,
                               IRT4M, lattice_pitch, LatticeUnitVR1)
from vr1.materials import VR1Materials
# Write an FA lattice, or teh core lattice, or the whole reactor
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
    def __init__(self, materials: VR1Materials):
        self.materials: VR1Materials = materials
        self.source_lower_left:  list[float] = [0, 0, 0]  # Boundaries for source
        self.source_upper_right: list[float] = [0, 0, 0]
        self.fa_type: (None, str) = None
        self.lattice = (None, openmc.RectLattice)
        self.model = openmc.Universe

    # def build_lattice_universes(self, lattice_str=(None, list[list[str]])):
    #     """ Loops over lattice """
    #     if self.lattice is None:
    #         raise ValueError('Lattice not defined')
    #     for row in lattice_str:
    #         for u in row:
    #             pass
    #
    def fuel_assembly(self, fa_type, boundaries='reflective'):
        """ Returns a fuel assembly """
        if fa_type not in list(lattice_unit_names.keys()):
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type = fa_type
        self.model = IRT4M(self.materials, self.fa_type, boundaries)
        self.source_lower_left = lattice_lower_left
        self.source_upper_right = lattice_upper_right

    def test_lattice(self, lattice_str=(None, list[list[str]])):
        if lattice_str is None:
            lattice_str = core_designs['small_test']
        n: int = len(lattice_str)
        assert n > 0
        for row in lattice_str:
            if len(row) != n:
                raise ValueError(f'{lattice_str} is not square')
        self.lattice = openmc.RectLattice()
        xy_corner: float = float(n) * lattice_pitch / 2.0
        self.lattice.lower_left = (-xy_corner, -xy_corner)
        self.lattice.pitch = lattice_pitch
        self.lattice.universes = np.empty((n, n), dtype=openmc.Universe)
        lattice_builder = LatticeUnitVR1(self.materials)
        for i in range(n):
            for j in range(n):
                u: str = lattice_str[i][j]
                self.lattice.universes[i][j] = lattice_builder.get(u)
        """ Lattice box """
        z0: float = plane_zs['FAZ2']
        z1: float = plane_zs['FAZ5']
        lattice_box = openmc.model.RectangularParallelepiped(-xy_corner, xy_corner, -xy_corner, xy_corner, z0, z1)
        lattice_cell = openmc.Cell(fill=self.lattice, region= -lattice_box)
        """ Water box around the lattice """
        x0: float = rects['CORE.rec'][0]
        x1: float = rects['CORE.rec'][1]
        y0: float = rects['CORE.rec'][2]
        y1: float = rects['CORE.rec'][3]
        z0: float = plane_zs['FAZ1']
        z1: float = plane_zs['FAZ6']
        core_box = openmc.model.RectangularParallelepiped(x0, x1, y0, y1, z0, z1)
        core_box.boundary_type = 'vacuum'
        self.model = openmc.Cell(fill=self.materials.water, region= -core_box & +lattice_box)
