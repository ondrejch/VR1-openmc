""" Lattice designs for VR1 """

import openmc
from vr1.materials import VR1Materials, vr1_materials

lattice_wh: float = 9.5  # Lattice unit width and height (X-Y) [cm]
lattice_pitch: float = 7.15  # Actual lattice pitch [cm]orca versus cura slicers

rects: dict = {
    "CORE.rec": {'width': 28.6- -28.6, 'height': 28.6- -28.6, 'axis': 'z', 
                'origin': [(28.6- -28.6)/2, (28.6- -28.6)/2]}, # concrete shielding
    "BOX.rec": {'width': 130- -130, 'height': 130- -215, 'axis': 'z', 
                'origin': [(130- -130)/2, (130- -215)/2], 'boundary_type': 'vacuum' } # concrete shielding
}

cones: dict = {
    "RCky.1": {'x0': 0, 'y0': -103.5, 'z0': 35.3, 'r2': 0.1162, 'up': -1}
}

sqcs: dict = {
    "1FT.1": {"wh": 6.964, "corner_r": 0.932},  # 1st tube outer cladding
    "1FT.2": {"wh": 6.87, "corner_r": 0.885},   # 1st tube outer fuel
    "1FT.3": {"wh": 6.73, "corner_r": 0.815},   # 1st tube inner fuel
    "1FT.4": {"wh": 6.636, "corner_r": 0.768},  # 1st tube outer cladding
    "2FT.1": {"wh": 6.274, "corner_r": 0.852},
    "2FT.2": {"wh": 6.18, "corner_r": 0.805},
    "2FT.3": {"wh": 6.04, "corner_r": 0.735},
    "2FT.4": {"wh": 5.946, "corner_r": 0.688},
    "3FT.1": {"wh": 5.584, "corner_r": 0.772},
    "3FT.2": {"wh": 5.49, "corner_r": 0.725},
    "3FT.3": {"wh": 5.35, "corner_r": 0.655},
    "3FT.4": {"wh": 5.256, "corner_r": 0.608},
    "4FT.1": {"wh": 4.894, "corner_r": 0.692},
    "4FT.2": {"wh": 4.8, "corner_r": 0.645},
    "4FT.3": {"wh": 4.66, "corner_r": 0.575},
    "4FT.4": {"wh": 4.566, "corner_r": 0.528},
    "5FT.1": {"wh": 4.204, "corner_r": 0.612},
    "5FT.2": {"wh": 4.11, "corner_r": 0.565},
    "5FT.3": {"wh": 3.97, "corner_r": 0.495},
    "5FT.4": {"wh": 3.876, "corner_r": 0.448},
    "6FT.1": {"wh": 3.514, "corner_r": 0.532},
    "6FT.2": {"wh": 3.42, "corner_r": 0.485},
    "6FT.3": {"wh": 3.28, "corner_r": 0.415},
    "6FT.4": {"wh": 3.186, "corner_r": 0.368},
    "7FT.1": {"wh": 2.824, "corner_r": 0.452},
    "7FT.2": {"wh": 2.73, "corner_r": 0.405},
    "7FT.3": {"wh": 2.59, "corner_r": 0.335},
    "7FT.4": {"wh": 2.496, "corner_r": 0.288},
    "ABS.1": {"wh": 2.800, "corner_r": 0.800},
    "DMY.1": {"wh": 3.500, "corner_r": 1.750},  # outer dim. fuel dummy rounding
    "DMY.2": {"wh": 3.350, "corner_r": 1.600},  # inner dim. fuel dummy rounding
    "ELE.1": {"wh": 3.575, "corner_r": 0.0},    # boundary 1 position
}

cyl_yz: dict = {

}

truncated_cyl_ys: dict = {
    "RCcy.1": {'x0': 0, 'z0': 35.3, 'r': 13.75, 'y': [-215,-21.45]},
    "RCcy.2": {"x0": 0, "z0": 35.3, "r": 12.55, "y": [-215, -22.45]},
    "RCcy.3": {"x0": 0, "z0": 35.3, "r": 12.35, "y": [-220, -22.65]},
    "RCcy.4": {"x0": 0, "z0": 35.3, "r": 11.35, "y": [-220, -24.65]},
    "RCcy.5": {"x0": 0, "z0": 35.3, "r": 4.9, "y": [-220, -24.65]},
    "RCcy.6": {"x0": 0, "z0": 35.3, "r": 4.5, "y": [-220, -22.65]},
    "RCcy.7": {"x0": 0, "z0": 35.3, "r": 3.9, "y": [-220, -24.65]},
    "RCcy.8": {"x0": 0, "z0": 35.3, "r": 16.0, "y": [-220, 0]},
    "RCcy.9": {"x0": 0, "z0": 35.3, "r": 17.5, "y": [-220, 0]},
    "RCcy.10": {"x0": 0, "z0": 35.3, "r": 21.0, "y": [-220, 0]},
    "RCcy.11": {"x0": 0, "z0": 35.3, "r": 15.0, "y": [-220, 0]},
    "RCcy.12": {"x0": 0, "z0": 35.3, "r": 20.0, "y": [-220, 0]},
    "RCcy.13": {"x0": 0, "z0": 35.3, "r": 21.0, "y": [-220, 0]}, #identical to RCcy.10 for some reason
    "RCcy.14": {"x0": 0, "z0": 35.3, "r": 22.5, "y": [-220, 0]}
    }

cyl_zs: dict = {
    "H01.2": 116.5,     # outer H01 vessel radius
    "H01.3": 120,       # inner H01 vessel shielding radius
    "8FT.1": 1.067,     # 8th tube outer cladding
    "8FT.2": 1.02,      # 8th tube outer fuel
    "8FT.3": 0.95,      # 8th tube inner fuel
    "8FT.4": 0.903,     # 8th tube inner cladding
    "H01.1": 115,       # inner side H01
    "DIS.1":  0.705,    # water displacer outer side
    "DIS.2":  0.605,    # water displacer inner side
    "ABS.2":  1.300,    # inner radius guide tube
    "ABS.3":  1.225,    # outer radius abs. tube
    "ABS.4":  1.000,    # outer radius Cd sheet
    "ABS.5":  0.900,    # outer radius Al core
    "DMP.1":  1.265,    # inner radius damper
    "C12.1":  0.700,    # outer radius channel 12 mm
    "C12.2":  0.600,    # inner radius channel 12 mm
    "C25.1":  1.250,    # outer radius channel 25 mm
    "C25.2":  1.150,    # inner radius channel 25 mm
    "C30.1":  1.500,    # outer radius channel 30 mm
    "C30.2":  1.400,    # inner radius channel 30 mm
    "C56.1":  3.500,    # outer radius channel 56 mm
    "C56.2":  3.000,    # inner radius channel 56 mm
    "C90.1":  5.500,    # outer radius channel 90 mm
    "C90.2":  5.000,    # inner radius channel 90 mm
    "RT.2":  1.2505,    # inner radius guide RT
    "RT.3":  1.1,       # outer radius channel RT
    "RT.4":  0.95,      # inner radius channel RT
    "GRD.1":  2.2,      # outer radius of core grid
    "GRD.2":  1.7,      # inner radius of core grid
    "Gr1.1":  {'x0': 1.8840, 'y0': 1.9275, 'r': 1.5770}, # upper right corner
    "Gr2.1":  {'x0': -1.8840, 'y0': 1.9275, 'r': 1.5770}, # upper left corner
    "Gr1.2":  {'x0': 1.8840, 'y0': 1.9275, 'r': 1.3070}, # upper right corner
    "Gr2.2":  {'x0': -1.8840, 'y0': 1.9275, 'r': 1.3070}, # upper left corner
    "Gr1.3":  {'x0': 1.8840, 'y0': 1.9275, 'r': 1.2000}, # upper right corner
    "Gr2.3":  {'x0': -1.8840, 'y0': 1.9275, 'r': 1.2000}, # upper left corner
}

truncated_cyl_zs: dict = {
    "RCcz.1": {"x0": 0, "y0": -138, "r": 4, "z": [35.3, 372]},
    "RCcz.2": {"x0": 0, "y0": -138, "r": 5, "z": [35.3, 372]},
    "RCcz.3": {"x0": 0, "y0": -200, "r": 4, "z": [35.3, 372]},
    "RCcz.4": {"x0": 0, "y0": -200, "r": 5, "z": [35.3, 372]}
}

plane_xs: dict = {
    "Gpx.1": -3.461,    # left (top) Al layer
    "Gpx.2":  3.461,    # right (top) Al layer
    "Gr1.x":  1.8840,   # support
    "Gr2.x": -1.8840,   # support
    "Gpx.3": -3.191,    # left (top) air layer
    "Gpx.4":  3.191,    # right (top) air layer
    "Gpx.5": -3.084,    # left (top) graphite layer
    "Gpx.6":  3.084,    # right (top) graphite layer
    "GRD.xp":  0.4,     # half pitch X of core grid
    "GRD.xn": -0.4,     # half pitch X of core grid
}

plane_ys: dict = {
    "Gpy.1":  3.5045,   # outter (top) Al layer
    "Gr.y":  1.9275,    # support
    "Gr2.y":  1.9275,   # support
    "Gpy.2":  3.2345,   # outter (top) air layer
    "Gpy.3":  3.1275,   # outter (top) graphite layer
    "GRD.yp":  0.4,     # half pitch Y of core grid
    "GRD.yn": -0.4,     # half pitch Y of core grid
    "RCpy.1": -86.5,    # inner face of radial channel flange
    "RCpy.2": -89.5,    # inner part of radial channel flange
    "RCpy.3": -93.5,    # outer part of radial channel flange
    "RCpy.4": -97.5,    # outer face of radial channel flange
    "RCpy.5": -102.3,   # outer limit of V2 plug
    "RCpy.6": -104.7,   # outer limit of V1/V3 plug
    "RCpy.7": -107.1,   # outer limit of V1/V3 plug
    "RCpy.8": -112.3,   # outer limit of wide V1/V3 plug
    "RCpy.9": -114.7,   # outer limit of wide V1/V3 plug
    "RCpy.10": -116.7,  # inner face of concrete plugs
    "RCpy.11": -170.5,  # interface of narrow/wide channel parts
    "RCpy.12": -172.5,  # interface of narrow/wide channel parts
}

plane_zs: dict = {
    "FAZ.1": 84.7,      # top edge of fuel header
    "FAZ.2": 73.0,      # top edge of fuel elements
    "FAZ.3": 66.4025,   # top edge of active fuel elements
    "FAZ.4": 7.5975,    # bottom edge of active fuel elements
    "FAZ.5": 1.0,       # bottom edge of fuel elements
    "FAZ.6": -3.5,      # bottom edge of fuel header
    "ELE.zp":  999.0,   # upper ax. boundary
    "ELE.zn": -999.0,   # lower ax. boundary
    "H01.zt":  {'z0': 372,'boundary_type':'vacuum'},     # upper edge boundary condition
    "H01.zd":  {'z0': -50.0,'boundary_type':'vacuum'},     # lower edge boundary condition
    "RB1.cd": 67.6,     # end of Cd sheet, move from set value by -0.4
    "RB2.cd": 67.6,     # end of Cd sheet, move from set value by -0.4
    "RB3.cd": 67.6,     # end of Cd sheet, move from set value by -0.4
    "RE1.cd": -0.4,     # end of Cd sheet, move from set value by -0.4
    "RE2.cd": 23.1,     # end of Cd sheet, move from set value by -0.4
    "RR1.cd": 37.8,     # end of Cd sheet, move from set value by -0.4
    "RR2.cd": 67.6,     # end of Cd sheet, move from set value by -0.4
    "RIN.cd": -0.4,     # end of Cd sheet, position for fully inserted rod, used in Xi models
    "RB1.hd": 60.5,     # end of rod head, height rod head 7.1
    "RB2.hd": 60.5,     # end of rod head, height rod head 7.1
    "RB3.hd": 60.5,     # end of rod head, height rod head 7.1
    "RE1.hd": -7.5,     # end of rod head, height rod head 7.1
    "RE2.hd": 16,       # end of rod head, height rod head 7.1
    "RR1.hd": 30.7,     # end of rod head, height rod head 7.1
    "RR2.hd": 60.5,     # end of rod head, height rod head 7.1
    "RIN.hd": -7.5,     # end of rod head, position for fully inserted rod, used in Xi models
    "CSM.z": -10.0,     # depth of small channels: 12, 25, 30
    "RT.zt": 30.699,    # upper insertion of PP
    "RT.zd": 28.699,    # lower insertion of PP
    "Gpz.1": 84.7,      # top end
    "Gpz.2": 71.5,      # top end of Al layer
    "Gpz.3": 71.3,      # top end of graphite
    "Gpz.4": 8.2,       # bottom end of graphite
    "Gpz.5": 7.5975,    # bottom end of Al layer
    "Gpz.6": -3.5,      # bottom end in grid
    "GRD.zt": 0,        # upper edge of core grid
    "GRD.zd": -7.51,    # lower edge of core grid
}

# ALL SURFACES ARE HERE
surfaces: dict = {}
for plane, z in plane_zs.items():
    if type(z) is dict:
        surfaces[plane] = openmc.ZPlane(name=plane, z0=z['z0'],boundary_type=z['boundary_type'])
    else:
        surfaces[plane] = openmc.ZPlane(name=plane, z0=z)
for plane, y in plane_ys.items():
    surfaces[plane] = openmc.YPlane(name=plane, y0=y)
for plane, x in plane_xs.items():
    surfaces[plane] = openmc.XPlane(name=plane, x0=x)
for k, sqc in sqcs.items():
    surfaces[k] = openmc.model.RectangularPrism(width=sqc['wh'], height=sqc['wh'], corner_radius=sqc['corner_r'])
for cyly, params in truncated_cyl_ys.items():
    surfaces[cyly] = openmc.model.RightCircularCylinder(name=cyly, center_base = [params['x0'],params['y'][0],params['z0']],radius=params['r'], axis = 'y', height = params['y'][1]-params['y'][0])
for cylz, param in cyl_zs.items():
    if type(param) is dict:
        surfaces[cylz] = openmc.ZCylinder(name=cylz,r=param['r'], x0=param['x0'], y0=param['y0'])
    else:
        surfaces[cylz] = openmc.ZCylinder(name=cylz, r=param)
for cylz, params in truncated_cyl_zs.items():
    #returns a region because openmc doesn't allow finite cylinders
    surfaces[cylz] = openmc.model.RightCircularCylinder(name=cylz, center_base = [params['x0'],params['y0'],params['z'][0]],radius=params['r'], height = params['z'][1]-params['z'][0])
for cone, params in cones.items():
    surfaces[cone] = openmc.model.YConeOneSided(x0=params['x0'], y0=params['y0'],z0=params['z0'],r2=params['r2'],up=params['up'])
for rect, params in rects.items():
    if 'boundary_type' in params:
        boundary_type = 'vacuum'
    else:
        boundary_type = 'transmission'
    surfaces[rect] = openmc.model.RectangularPrism(width=params['width'],height=params['height'],origin=params['origin'],boundary_type=boundary_type)

lattice_unit_names: dict[str:str] = {
    '8': '8-tube FA',
    '6': '6-tube FA',
    '4': '4-tube FA',
    # 'O': '6-tube FA with a fully withdrawn control rod',
    # 'X': '6-tube FA with a fully inserted control rod',
    # 'R1': '6-tube FA with regulatory control rod 1',
    # 'R2': '6-tube FA with regulatory control rod 2',
    # 'E1': '6-tube FA with experimental shim rod 2',
    # 'E2': '6-tube FA with experimental shim rod 2',
    # 'E3': '6-tube FA with experimental shim rod 2',
    # 'd': 'Empty fuel dummy',
    # 'w': 'Empty water cell',
}

lattice_unit_boundaries: list[str] = [
    'reflective',  # Reflective
    'water'        # Surrounded by water
]

# Lattice active fuel boundary for source definition
lattice_lower_left: list[float] = [-lattice_wh / 2.0, -lattice_wh / 2.0, plane_zs['FAZ.4']]
lattice_upper_right: list[float] = [lattice_wh / 2.0, lattice_wh / 2.0, plane_zs['FAZ.3']]


class LatticeUnitVR1:
    """ Virtual base class """
    def __init__(self,materials):
        self.materials = materials
        self.cells: dict = {}

    def name(self) -> str:
        return "Lattice Unit VR1 base class"

    def get(self, lattice_code: str = 'w') -> openmc.Universe():
        lattice_unit_builders: dict = {
            '8': IRT4M(fa_type='8',materials=self.materials),
            '6': IRT4M(fa_type='6',materials=self.materials),
            '4': IRT4M(fa_type='4',materials=self.materials),
        # 'O': '6-tube FA with a fully withdrawn control rod',
        # 'X': '6-tube FA with a fully inserted control rod',
        # 'R1': '6-tube FA with regulatory control rod 1',
        # 'R2': '6-tube FA with regulatory control rod 2',
        # 'E1': '6-tube FA with experimental shim rod 2',
        # 'E2': '6-tube FA with experimental shim rod 2',
        # 'E3': '6-tube FA with experimental shim rod 2',
        # 'd': 'Empty fuel dummy',
            'w': Water(materials=self.materials),
        }
        return lattice_unit_builders[lattice_code].build()


class Water(LatticeUnitVR1):
    """ Water lattice unit """
    def __init__(self, materials : VR1Materials = vr1_materials):
        super().__init__(materials)

    def name(self) -> str:
        return "Water filling the lattice"

    def build(self) -> openmc.Universe:
        self.cells['water'] = openmc.Cell(name='water', fill=self.materials.water, region=-surfaces['ELE.1'])  # & -surfaces['ELE.zp'] & surfaces['GRD.zt'])
        return openmc.Universe(name='water', cells=list(self.cells.values()))


class IRT4M(LatticeUnitVR1):
    """ Class that returns IRT4M fuel units """
    def __init__(self, fa_type: str, materials: VR1Materials = vr1_materials, boundary: str = 'water') -> None:
        super().__init__(materials)
        if boundary not in lattice_unit_boundaries:
            raise ValueError(f'boundary {boundary} is not valid')
        self.boundary: str = boundary
        self.known_fuel_assemblies: list[str] = list(lattice_unit_names.keys())
        if fa_type not in self.known_fuel_assemblies:
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type: str = fa_type

    def name(self) -> str:
        """ Returns the name of the FA lattice """
        return lattice_unit_names[self.fa_type]

    def build(self) -> openmc.Universe:
        """ Builds an IRT4M fuel assembly lattice until. TODO: control rod lattices """
        n_plates: int = int(lattice_unit_names[self.fa_type][0])  # How many plates in the FA
        """ FA surfaces """
        surfaces['boundary_XY'] = openmc.model.RectangularPrism(width=lattice_wh, height=lattice_wh)
        if self.boundary == 'reflective':
            surfaces['boundary_XY'].boundary_type = 'reflective'
            surfaces['FAZ.2'].boundary_type = 'reflective'
            surfaces['FAZ.4'].boundary_type = 'reflective'

        """ Common FA cells """
        self.cells['out_top'] = openmc.Cell(name='out_top', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT.1'] & -surfaces['FAZ.2'] & +surfaces['FAZ.3'])
        self.cells['out_mid'] = openmc.Cell(name='out_mid', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT.1'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
        self.cells['out_bot'] = openmc.Cell(name='out_bot', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])

        for i in range(1, n_plates):
            self.cells[f'top_c_{i}'] = openmc.Cell(name=f'top_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.2'] & +surfaces['FAZ.3'])
            self.cells[f'top_w_{i}'] = openmc.Cell(name=f'top_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & +surfaces[f'{i + 1}FT.1'] & -surfaces['FAZ.2'] & +surfaces['FAZ.3'])

            self.cells[f'mid_c_{i}'] = openmc.Cell(name=f'mid_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.2'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
            self.cells[f'mid_f_{i}'] = openmc.Cell(name=f'mid_f_{i}', fill=self.materials.fuel, region=-surfaces[f'{i}FT.2'] & +surfaces[f'{i}FT.3'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
            self.cells[f'mid_i_{i}'] = openmc.Cell(name=f'mid_i_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.3'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
            self.cells[f'mid_w_{i}'] = openmc.Cell(name=f'mid_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & +surfaces[f'{i + 1}FT.1'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])

            self.cells[f'bot_c_{i}'] = openmc.Cell(name=f'bot_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
            self.cells[f'bot_w_{i}'] = openmc.Cell(name=f'bot_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & +surfaces[f'{i + 1}FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])

        i = n_plates
        self.cells[f'top_c_{i}'] = openmc.Cell(name=f'top_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.2'] & +surfaces['FAZ.3'])
        self.cells[f'top_w_{i}'] = openmc.Cell(name=f'top_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & -surfaces['FAZ.2'] & +surfaces['FAZ.3'])

        self.cells[f'mid_c_{i}'] = openmc.Cell(name=f'mid_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.2'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
        self.cells[f'mid_f_{i}'] = openmc.Cell(name=f'mid_f_{i}', fill=self.materials.fuel, region=-surfaces[f'{i}FT.2'] & +surfaces[f'{i}FT.3'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
        self.cells[f'mid_i_{i}'] = openmc.Cell(name=f'mid_i_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.3'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])
        self.cells[f'mid_w_{i}'] = openmc.Cell(name=f'mid_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & -surfaces['FAZ.3'] & +surfaces['FAZ.4'])

        self.cells[f'bot_c_{i}'] = openmc.Cell(name=f'bot_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT.1'] & +surfaces[f'{i}FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'bot_w_{i}'] = openmc.Cell(name=f'bot_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])

        self.cells[f'0.8.60']    = openmc.Cell(name=f'0.8.60', fill=self.materials.water,   region=-surfaces['1FT.1'] & -surfaces['ELE.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.61']    = openmc.Cell(name=f'0.8.61', fill=self.materials.cladding,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.62']    = openmc.Cell(name=f'0.8.62', fill=self.materials.water,   region=-surfaces['1FT.4'] & +surfaces['2FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.63']    = openmc.Cell(name=f'0.8.63', fill=self.materials.cladding,region=-surfaces['2FT.1'] & +surfaces['2FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.64']    = openmc.Cell(name=f'0.8.64', fill=self.materials.water,   region=-surfaces['2FT.4'] & +surfaces['3FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.65']    = openmc.Cell(name=f'0.8.65', fill=self.materials.cladding,region=-surfaces['3FT.1'] & +surfaces['3FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.66']    = openmc.Cell(name=f'0.8.66', fill=self.materials.water,   region=-surfaces['3FT.4'] & +surfaces['4FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.67']    = openmc.Cell(name=f'0.8.67', fill=self.materials.cladding,region=-surfaces['4FT.1'] & +surfaces['4FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.68']    = openmc.Cell(name=f'0.8.68', fill=self.materials.water,   region=-surfaces['4FT.4'] & +surfaces['5FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.69']    = openmc.Cell(name=f'0.8.69', fill=self.materials.cladding,region=-surfaces['5FT.1'] & +surfaces['5FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.70']    = openmc.Cell(name=f'0.8.70', fill=self.materials.water,   region=-surfaces['5FT.4'] & +surfaces['6FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.71']    = openmc.Cell(name=f'0.8.71', fill=self.materials.cladding,region=-surfaces['6FT.1'] & +surfaces['6FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.72']    = openmc.Cell(name=f'0.8.72', fill=self.materials.water,   region=-surfaces['6FT.4'] & +surfaces['7FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.73']    = openmc.Cell(name=f'0.8.73', fill=self.materials.cladding,region=-surfaces['7FT.1'] & +surfaces['7FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.74']    = openmc.Cell(name=f'0.8.74', fill=self.materials.water,   region=-surfaces['7FT.4'] & +surfaces['8FT.1'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.75']    = openmc.Cell(name=f'0.8.75', fill=self.materials.cladding,region=-surfaces['8FT.1'] & +surfaces['8FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])
        self.cells[f'0.8.76']    = openmc.Cell(name=f'0.8.76', fill=self.materials.water,   region=-surfaces['8FT.4'] & -surfaces['FAZ.4'] & +surfaces['FAZ.5'])

        self.cells[f'0.8.78']    = openmc.Cell(name=f'0.8.78', fill=self.materials.water,   region=+surfaces['1FT.1'] & -surfaces['FAZ.5'] & +surfaces['GRD.zt'] & -surfaces['ELE.1'])
        self.cells[f'0.8.79']    = openmc.Cell(name=f'0.8.79', fill=self.materials.cladding,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & -surfaces['FAZ.5'] & +surfaces['GRD.zt'])
        self.cells[f'0.8.80']    = openmc.Cell(name=f'0.8.80', fill=self.materials.water,   region=-surfaces['1FT.4'] & -surfaces['FAZ.5'] & +surfaces['GRD.zt'])


        self.cells[f'0.8.82']    = openmc.Cell(name=f'0.8.82', fill=self.materials.water,region=-surfaces['1FT.4'] & +surfaces['GRD.xp'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.83']    = openmc.Cell(name=f'0.8.83', fill=self.materials.water,region=-surfaces['1FT.4'] & +surfaces['GRD.xp'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.84']    = openmc.Cell(name=f'0.8.84', fill=self.materials.water,region=-surfaces['1FT.4'] & -surfaces['GRD.xn'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.85']    = openmc.Cell(name=f'0.8.85', fill=self.materials.water,region=-surfaces['1FT.4'] & -surfaces['GRD.xn'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.86']    = openmc.Cell(name=f'0.8.86', fill=self.materials.water,region=+surfaces['1FT.1'] & +surfaces['GRD.xp'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.87']    = openmc.Cell(name=f'0.8.87', fill=self.materials.water,region=+surfaces['1FT.1'] & +surfaces['GRD.xp'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.88']    = openmc.Cell(name=f'0.8.88', fill=self.materials.water,region=+surfaces['1FT.1'] & -surfaces['GRD.xn'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.89']    = openmc.Cell(name=f'0.8.89', fill=self.materials.water,region=+surfaces['1FT.1'] & -surfaces['GRD.xn'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'] & -surfaces['ELE.1'])
        self.cells[f'0.8.90']    = openmc.Cell(name=f'0.8.90', fill=self.materials.bottomnozzle,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & +surfaces['GRD.xp'] & +surfaces['GRD.yp'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.91']    = openmc.Cell(name=f'0.8.91', fill=self.materials.bottomnozzle,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & +surfaces['GRD.xp'] & -surfaces['GRD.yn'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.92']    = openmc.Cell(name=f'0.8.92', fill=self.materials.bottomnozzle,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & -surfaces['GRD.xn'] & +surfaces['GRD.yp'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.93']    = openmc.Cell(name=f'0.8.93', fill=self.materials.bottomnozzle,region=-surfaces['1FT.1'] & +surfaces['1FT.4'] & -surfaces['GRD.xn'] & -surfaces['GRD.yn'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.94']    = openmc.Cell(name=f'0.8.94', fill=self.materials.grid,region=-surfaces['GRD.1']  & +surfaces['GRD.2'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.95']    = openmc.Cell(name=f'0.8.95', fill=self.materials.grid,region=-surfaces['GRD.xp'] & +surfaces['GRD.xn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.96']    = openmc.Cell(name=f'0.8.96', fill=self.materials.grid,region=-surfaces['GRD.yp'] & +surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])
        self.cells[f'0.8.97']    = openmc.Cell(name=f'0.8.97', fill=self.materials.water,region=-surfaces['GRD.2'] & -surfaces['GRD.zt'] & +surfaces['FAZ.6'])

        self.cells[f'0.8.99']    = openmc.Cell(name=f'0.8.99', fill=self.materials.water,region=+surfaces['GRD.xp'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.100']   = openmc.Cell(name=f'0.8.100',fill=self.materials.water,region=+surfaces['GRD.xp'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.101']   = openmc.Cell(name=f'0.8.101',fill=self.materials.water,region=-surfaces['GRD.xn'] & +surfaces['GRD.yp'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.102']   = openmc.Cell(name=f'0.8.102',fill=self.materials.water,region=-surfaces['GRD.xn'] & -surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.103']   = openmc.Cell(name=f'0.8.103',fill=self.materials.grid ,region=-surfaces['GRD.1'] & +surfaces['GRD.2'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.104']   = openmc.Cell(name=f'0.8.104',fill=self.materials.grid ,region=-surfaces['GRD.xp'] & +surfaces['GRD.xn'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.105']   = openmc.Cell(name=f'0.8.105',fill=self.materials.grid ,region=-surfaces['GRD.yp'] & +surfaces['GRD.yn'] & +surfaces['GRD.1'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'] & -surfaces['ELE.1'])
        self.cells[f'0.8.106']   = openmc.Cell(name=f'0.8.106',fill=self.materials.water,region=-surfaces['GRD.2'] & -surfaces['FAZ.6'] & +surfaces['GRD.zd'])

        self.cells[f'0.8.108']   = openmc.Cell(name=f'0.8.108',fill=self.materials.water,region=-surfaces['GRD.zd'] & +surfaces['ELE.zn'] & -surfaces['ELE.1'])


        return openmc.Universe(name=f'lattice_{lattice_unit_names[self.fa_type]}', cells=list(self.cells.values()))


class AbsRod(LatticeUnitVR1):
    """ Class that returns absorption rod units """
    def __init__(self, materials : VR1Materials = vr1_materials, boundary: str = 'water') -> None:
        super().__init__(materials)
        if boundary not in lattice_unit_boundaries:
            raise ValueError(f'boundary {boundary} is not valid')
        self.boundary: str = boundary

    def name(self) -> str:
        """ Returns the name of the rod """
        return 'Cadmium absorption rod'

    def build(self, rod_height: float = 0.0) -> openmc.Universe:
        """ Builds an absorption rod """
        """ Absorption rod surfaces """
        surfaces['boundary_XY'] = surfaces['ABS.1']
        lower_bound = openmc.ZPlane(z0=plane_zs['GRD.zd'] + rod_height) #adjusting control rod from listed position

        if self.boundary == 'reflective':
            surfaces['boundary_XY'].boundary_type = 'reflective'
            surfaces['ELE.zp'].boundary_type = 'reflective'
            surfaces['GRD.zt'].boundary_type = 'reflective'

        """ Building Absorber Rod """

        cell_0Guidetube_1 = openmc.Cell(fill=self.materials.water,     region=-surfaces['ABS.1'] & +surfaces['ABS.2'])
        cell_0Guidetube_2 = openmc.Cell(fill=self.materials.guidetube, region=-surfaces['ABS.2'] & +surfaces['ABS.3'])

        universe_0Guidetube = openmc.Universe(cells=[cell_0Guidetube_1, cell_0Guidetube_2])
        self.cells['Guidetube'] = openmc.Cell(fill=universe_0Guidetube, region=-surfaces['ABS.1'] & +surfaces['ABS.3'] & -surfaces['ELE.zp'] & +surfaces['GRD.zt'])

        cell_0Absrod_1 = openmc.Cell(fill=self.materials.abstube,   region=-surfaces['ABS.3'] & +surfaces['ABS.4'] & +surfaces['RB1.cd'])
        cell_0Absrod_2 = openmc.Cell(fill=self.materials.cdlayer,   region=-surfaces['ABS.4'] & +surfaces['ABS.5'] & +surfaces['RB1.cd'])
        cell_0Absrod_3 = openmc.Cell(fill=self.materials.abscenter, region=-surfaces['ABS.5'] & +surfaces['RB1.cd'])
        cell_0Absrod_4 = openmc.Cell(fill=self.materials.abshead,   region=-surfaces['ABS.3'] & -surfaces['RB1.cd'] & +surfaces['RB1.hd'])
        cell_0Absrod_5 = openmc.Cell(fill=self.materials.water,     region=-surfaces['ABS.3'] & -surfaces['RB1.hd'])

        universe_0Absrod = openmc.Universe(cells=[cell_0Absrod_1,cell_0Absrod_2,cell_0Absrod_3,cell_0Absrod_4,cell_0Absrod_5])
        self.cells['Absrod'] = openmc.Cell(fill=universe_0Absrod,region=-surfaces['ABS.3'] & -surfaces['ELE.zp'] & +lower_bound)

        self.cells['Plenum'] = openmc.Cell(fill=self.materials.air, region=-surfaces['ABS.3'] & -lower_bound & + surfaces['GRD.zt'])

        return openmc.Universe(name="abs_rod", cells=list(self.cells.values()))

""" Shell scripts to extract surfaces from the Serpent model """
# grep ' px ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ px/":\ /g' -e s/\ %/,\ #/g
# grep ' py ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ py/":\ /g' -e s/\ %/,\ #/g
# grep ' pz ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ pz/":\ /g' -e s/\ %/,\ #/g
# grep ' cyl ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ cyl/":\ /g' -e s/\ %/,\ #/g -e s/0\ 0\ //g
# grep ' rect ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ rect/":\ /g' -e s/\ %/,\ #/g -e s/0\ 0\ //g
# grep ' cylz ' C12-C-2023_1| sed -e 's/surf\ /\ \ \ \ "/g' -e 's/\ cylz/":\ /g' -e s/\ %/,\ #/g -e s/0\ 0\ //g
