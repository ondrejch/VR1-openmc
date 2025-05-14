""" Lattice designs for VR1 """

import openmc
from vr1.materials import VR1Materials

lattice_wh: float = 9.5  # Lattice unit width and height (X-Y) [cm]
lattice_pitch: float = 7.15  # Actual lattice pitch [cm]orca versus cura slicers


fuel_sqc: dict = {
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
}

cyl_zs: dict = {
    "8FT.1": 1.067, # 8th tube outer cladding
    "8FT.2": 1.02,  # 8th tube outer fuel
    "8FT.3": 0.95,  # 8th tube inner fuel
    "8FT.4": 0.903, # 8th tube inner cladding
    "H01.1": 115,  # inner side H01
    "DIS.1":  0.705, # water displacer outer side
    "DIS.2":  0.605, # water displacer inner side
    "ABS.2":  1.300, # inner radius guide tube
    "ABS.3":  1.225, # outer radius abs. tube
    "ABS.4":  1.000, # outer radius Cd sheet
    "ABS.5":  0.900, # outer radius Al core
    "DMP.1":  1.265, # inner radius damper
    "C12.1":  0.700, # outer radius channel 12 mm
    "C12.2":  0.600, # inner radius channel 12 mm
    "C25.1":  1.250, # outer radius channel 25 mm
    "C25.2":  1.150, # inner radius channel 25 mm
    "C30.1":  1.500, # outer radius channel 30 mm
    "C30.2":  1.400, # inner radius channel 30 mm
    "C56.1":  3.500, # outer radius channel 56 mm
    "C56.2":  3.000, # inner radius channel 56 mm
    "C90.1":  5.500, # outer radius channel 90 mm
    "C90.2":  5.000, # inner radius channel 90 mm
    "RT.2":  1.2505, # inner radius guide RT
    "RT.3":  1.1, # outer radius channel RT
    "RT.4":  0.95, # inner radius channel RT
    # "Gr1.1":  1.8840 1.9275 1.5770, # upper right corner
    # "Gr2.1":  -1.8840 1.9275 1.5770, # upper left corner
    # "Gr1.2":  1.8840 1.9275 1.3070, # upper right corner
    # "Gr2.2":  -1.8840 1.9275 1.3070, # upper left corner
    # "Gr1.3":  1.8840 1.9275 1.2000, # upper right corner
    # "Gr2.3":  -1.8840 1.9275 1.2000, # upper left corner
    "GRD.1":  2.2, # outer radius of core grid
    "GRD.2":  1.7, # inner radius of core grid
    # "RCcz.1":  0 -138 4 35.3 372, # inside vertical channel in radial channel inner radius (estimation)
    # "RCcz.2":  0 -138 5 35.3 372, # inside vertical channel in radial channel outer radius (estimation)
    # "RCcz.3":  0 -200 4 35.3 372, # outside vertical channel in radial channel inner radius (estimation)
    # "RCcz.4":  0 -200 5 35.3 372, # outside vertical channel in radial channel outer radius (estimation)
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
    "H01.zt":  372,     # upper edge boundary condition
    "H01.zd":  -50,     # lower edge boundary condition
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

dummy_sqcs: dict = {
    "DMY.1": {"wh": 3.500, "corner_r": 1.750},  # outer dim. fuel dummy rounding
    "DMY.2": {"wh": 3.350, "corner_r": 1.600},  # inner dim. fuel dummy rounding
    "ELE.1": {"wh": 3.575, "corner_r": 0.0},    # boundary 1 position
}

# ALL SURFACES ARE HERE
surfaces: dict = {}
for plane, z in plane_zs.items():
    surfaces[plane] = openmc.ZPlane(name=plane, z0=z)
for sqc, v in fuel_sqc.items():
    surfaces[sqc] = openmc.model.RectangularPrism(width=sqc['wh'], height=sqc['wh'], corner_radius=sqc['corner_r'])
for cylz, r in cyl_zs.items():
    surfaces[cylz] = openmc.ZCylinder(name=cylz, r=r)

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


class IRT4M:
    """ Class that returns IRT4M fuel units """
    def __init__(self, materials: VR1Materials, fa_type: str, boundary: str) -> None:
        if boundary not in lattice_unit_boundaries:
            raise ValueError(f'boundary {boundary} is not valid')
        self.boundary: str = boundary
        self.known_fuel_assemblies: list[str] = list(lattice_unit_names.keys())
        if fa_type not in self.known_fuel_assemblies:
            raise ValueError(f'{fa_type} is not a known lattice unit type!')
        if 'FA' not in lattice_unit_names[fa_type]:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type: str = fa_type
        self.materials = materials
        self.cells: dict = {}

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
            surfaces['FAZ2'].boundary_type = 'reflective'  # TODO - change to FAZ 1 an 6 once these are implemented.
            surfaces['FAZ6'].boundary_type = 'reflective'  #

        """ Common FA cells """
        self.cells['out_top'] = openmc.Cell(name='out_top', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT1'] & -surfaces['FAZ2'] & +surfaces['FAZ3'])
        self.cells['out_mid'] = openmc.Cell(name='out_mid', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT1'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
        self.cells['out_bot'] = openmc.Cell(name='out_bot', fill=self.materials.water, region=-surfaces['boundary_XY'] & +surfaces['1FT1'] & -surfaces['FAZ4'] & +surfaces['FAZ5'])

        for i in range(1, n_plates-1):
            self.cells[f'top_c_{i}'] = openmc.Cell(name=f'top_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ2'] & +surfaces['FAZ3'])
            self.cells[f'top_w_{i}'] = openmc.Cell(name=f'top_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & +surfaces[f'{i + 1}FT1'] & -surfaces['FAZ2'] & +surfaces['FAZ3'])

            self.cells[f'mid_c_{i}'] = openmc.Cell(name=f'mid_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT2'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
            self.cells[f'mid_f_{i}'] = openmc.Cell(name=f'mid_f_{i}', fill=self.materials.fuel, region=-surfaces[f'{i}FT2'] & +surfaces[f'{i}FT3'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
            self.cells[f'mid_i_{i}'] = openmc.Cell(name=f'mid_i_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT3'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
            self.cells[f'mid_w_{i}'] = openmc.Cell(name=f'mid_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & +surfaces[f'{i + 1}FT1'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])

            self.cells[f'bot_c_{i}'] = openmc.Cell(name=f'bot_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ4'] & +surfaces['FAZ5'])
            self.cells[f'bot_w_{i}'] = openmc.Cell(name=f'bot_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & +surfaces[f'{i + 1}FT1'] & -surfaces['FAZ4'] & +surfaces['FAZ5'])

        i = n_plates
        self.cells[f'top_c_{i}'] = openmc.Cell(name=f'top_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ2'] & +surfaces['FAZ3'])
        self.cells[f'top_w_{i}'] = openmc.Cell(name=f'top_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & -surfaces['FAZ2'] & +surfaces['FAZ3'])

        self.cells[f'mid_c_{i}'] = openmc.Cell(name=f'mid_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT2'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
        self.cells[f'mid_f_{i}'] = openmc.Cell(name=f'mid_f_{i}', fill=self.materials.fuel, region=-surfaces[f'{i}FT2'] & +surfaces[f'{i}FT3'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
        self.cells[f'mid_i_{i}'] = openmc.Cell(name=f'mid_i_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT3'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])
        self.cells[f'mid_w_{i}'] = openmc.Cell(name=f'mid_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & -surfaces['FAZ3'] & +surfaces['FAZ4'])

        self.cells[f'bot_c_{i}'] = openmc.Cell(name=f'bot_c_{i}', fill=self.materials.cladding, region=-surfaces[f'{i}FT1'] & +surfaces[f'{i}FT4'] & -surfaces['FAZ4'] & +surfaces['FAZ5'])
        self.cells[f'bot_w_{i}'] = openmc.Cell(name=f'bot_w_{i}', fill=self.materials.water, region=-surfaces[f'{i}FT4'] & -surfaces['FAZ4'] & +surfaces['FAZ5'])

        return openmc.Universe(self.cells)
