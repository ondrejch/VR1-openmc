""" Core design for VR1 """
import openmc
from vr1.materials import vr1_materials
from vr1.lattice_units import (rects, plane_zs, lattice_unit_names, lattice_lower_left, lattice_upper_right,
                               IRT4M, lattice_pitch, LatticeUnitVR1)
from vr1.lattice_units import surfaces

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

class VR1facility(VR1core):
    def __init__(self, lattice_str: (None, list[list[str]]) = None):
        super().__init__()
        if lattice_str is None:
            lattice_str = core_designs['small_test']
        self.lattice = TestLattice(lattice_str)
        self.surfaces = surfaces
        self.cells = {}
    
    def build(self) -> openmc.Universe:
        self.cells["surf.1"] = openmc.Cell(name="surf.1", fill = self.materials.radialchannel, region=self.surfaces["RCcy.1"] & ~self.surfaces["RCcy.2"] & +self.surfaces["RCpy.2"])
        self.cells["water.1"] = openmc.Cell(name="water.1", fill = self.materials.water, region=-self.surfaces["H01.1"] & +self.surfaces["CORE.rec"] & ~self.surfaces["RCcy.1"] & +self.surfaces["RCpy.1"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["water.2"] = openmc.Cell(name="water.2", fill = self.materials.water, region=-self.surfaces["H01.1"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.4"] & ~self.surfaces["RCcy.10"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["water.3"] = openmc.Cell(name="water.3", fill = self.materials.water, region=-self.surfaces["H01.1"] & -self.surfaces["RCpy.4"] & ~self.surfaces["RCcy.8"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["OUTrk17"] = openmc.Cell(name="OUTrk17", fill = self.materials.steelrc, region=self.surfaces["RCcy.9"] & ~self.surfaces["RCcy.1"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.2"])
        self.cells["OUTrk16"] = openmc.Cell(name="OUTrk16", fill = self.materials.steelrc, region=self.surfaces["RCcy.10"] & ~self.surfaces["RCcy.9"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.4"])
        self.cells["OUTrk18"] = openmc.Cell(name="OUTrk18", fill = self.materials.steelrc, region=self.surfaces["RCcy.9"] & ~self.surfaces["RCcy.2"] & -self.surfaces["RCpy.3"] & +self.surfaces["RCpy.4"])
        self.cells["OUTrk20"] = openmc.Cell(name="OUTrk20", fill = self.materials.radialchannel, region=self.surfaces["RCcy.9"] & ~self.surfaces["RCcy.2"] & -self.surfaces["RCpy.2"] & +self.surfaces["RCpy.3"])
        self.cells["OUTrk22"] = openmc.Cell(name="OUTrk22", fill = self.materials.steelrc, region=self.surfaces["RCcy.8"] & ~self.surfaces["RCcy.1"] & -self.surfaces["RCpy.4"] & -self.surfaces["H01.1"])
        self.cells["OUTrk22"] = openmc.Cell(name="OUTrk22", fill = self.materials.steelrc, region=self.surfaces["RCcy.8"] & ~self.surfaces["RCcy.1"] & -self.surfaces["RCpy.4"] & -self.surfaces["H01.1"])
        self.cells["OUTrk23"] = openmc.Cell(name="OUTrk23", fill = self.materials.radialchannel, region=self.surfaces["RCcy.1"] & ~self.surfaces["RCcy.2"] & -self.surfaces["RCpy.4"] & +self.surfaces["RCpy.12"] & ~self.surfaces["RCcz.2"])
        self.cells["OUTrk57"] = openmc.Cell(name="OUTrk57", fill = self.materials.lead, region=-self.surfaces["RCpy.10"] & +self.surfaces["RCpy.11"] & ~self.surfaces["RCcy.1"] & self.surfaces["RCcy.11"] & ~self.surfaces["RCcz.2"] & +self.surfaces["H01.3"])
        self.cells["OUTrk58"] = openmc.Cell(name="OUTrk58", fill = self.materials.lead, region=-self.surfaces["RCpy.10"] & +self.surfaces["RCpy.11"] & -self.surfaces["RCky.1"] & self.surfaces["RCcy.14"] & ~self.surfaces["RCcy.11"])
        self.cells["OUTrk61P1"] = openmc.Cell(name="OUTrk61P1", fill = self.materials.steelrc, region=self.surfaces["RCcz.2"] & ~self.surfaces["RCcz.1"] & -self.surfaces["H01.zt"] & ~self.surfaces["RCcy.2"])
        self.cells["OUTrk62P1"] = openmc.Cell(name="OUTrk62P1", fill = self.materials.air, region=self.surfaces["RCcz.1"] & ~self.surfaces["RCcy.2"] & -self.surfaces["H01.zt"])
        self.cells["OUTrk66"] = openmc.Cell(name="OUTrk66", fill = self.materials.lead, region=self.surfaces["RCcy.14"] & ~self.surfaces["RCcy.13"] & -self.surfaces["RCpy.11"] & +self.surfaces["RCpy.12"])
        self.cells["OUTrk67"] = openmc.Cell(name="OUTrk67", fill = self.materials.radialchannel, region=self.surfaces["RCcy.13"] & ~self.surfaces["RCcy.1"] & -self.surfaces["RCpy.11"] & +self.surfaces["RCpy.12"])
        self.cells["OUTrk61P2"] = openmc.Cell(name="OUTrk61P2", fill = self.materials.steelrc, region=self.surfaces["RCcz.4"] & ~self.surfaces["RCcz.3"] & -self.surfaces["H01.zt"] & ~self.surfaces["RCcy.12"])
        self.cells["OUTrk62P2"] = openmc.Cell(name="OUTrk62P2", fill = self.materials.air, region=self.surfaces["RCcz.3"] & ~self.surfaces["RCcy.12"] & -self.surfaces["H01.zt"])
        self.cells["OUTrk90"] = openmc.Cell(name="OUTrk90", fill = self.materials.lead, region=-self.surfaces["RCpy.12"] & -self.surfaces["BOX.rec"] & self.surfaces["RCcy.14"] & ~self.surfaces["RCcy.13"] & ~self.surfaces["RCcz.4"])
        self.cells["OUTrk91"] = openmc.Cell(name="OUTrk91", fill = self.materials.radialchannel, region=-self.surfaces["RCpy.12"] & -self.surfaces["BOX.rec"] & self.surfaces["RCcy.13"] & ~self.surfaces["RCcy.12"] & ~self.surfaces["RCcz.4"])
        self.cells["HO1vsl1"] = openmc.Cell(name="HO1vsl1", fill = self.materials.vessel, region=-self.surfaces["H01.2"] & +self.surfaces["H01.1"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & ~self.surfaces["RCcy.1"])
        self.cells["HO1vsl2"] = openmc.Cell(name="HO1vsl2", fill = None, region=-self.surfaces["H01.3"] & +self.surfaces["H01.2"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & ~self.surfaces["RCcy.1"])
        self.cells["SHIELD1"] = openmc.Cell(name="SHIELD1", fill = self.materials.concrete, region=-self.surfaces["BOX.rec"] & +self.surfaces["H01.3"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & ~self.surfaces["RCcy.14"] & ~self.surfaces["RCcz.2"] & ~self.surfaces["RCcz.4"])
        self.cells["SHIELD2"] = openmc.Cell(name="SHIELD2", fill = self.materials.concrete, region=-self.surfaces["BOX.rec"] & +self.surfaces["H01.3"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & self.surfaces["RCcy.14"] & +self.surfaces["RCky.1"] & ~self.surfaces["RCcy.11"] & ~self.surfaces["RCcz.2"] & ~self.surfaces["RCcz.4"])
        self.cells["OUT.1"] = openmc.Cell(name="OUT.1", fill = self.materials.outside, region=+self.surfaces["BOX.rec"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["OUT.2"] = openmc.Cell(name="OUT.2", fill = self.materials.outside, region=+self.surfaces["H01.zt"])
        self.cells["OUT.3"] = openmc.Cell(name="OUT.3", fill = self.materials.outside, region=-self.surfaces["H01.zd"])
        self.cells["V2.1"] = openmc.Cell(name="V2.1", fill = self.materials.air, region=self.surfaces["RCcy.2"] & ~self.surfaces["RCcy.3"] & +self.surfaces["RCpy.9"])
        return openmc.Universe(name="facility", cells=list(self.cells.values()))

