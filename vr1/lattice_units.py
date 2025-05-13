import openmc
from materials import VR1Material

lattice_wh: float = 9.5

rounded_rectangles: dict = {
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
}

# surf_FAZ1 = srp_to_omc('surf FAZ.1 pz 84.7 % top edge of fuel header').omc_surface()
# surf_FAZ2 = openmc.ZPlane(z0=73, boundary_type='vacuum')
# # surf_FAZ2 = srp_to_omc('surf FAZ.2 pz 73.0000 % top edge of fuel elements').omc_surface()
# surf_FAZ3 = srp_to_omc('surf FAZ.3 pz 66.4025 % top edge of active fuel elements').omc_surface()
# surf_FAZ4 = srp_to_omc('surf FAZ.4 pz 7.5975 % bottom edge of active fuel elements').omc_surface()
# # surf_FAZ5 = srp_to_omc('surf FAZ.5 pz 1.0 % bottom edge of fuel elements').omc_surface()
# surf_FAZ5 = openmc.ZPlane(z0=1, boundary_type='vacuum')
# surf_FAZ6 = srp_to_omc('surf FAZ.6 pz -3.5 % bottom edge of fuel header').omc_surface()
plane_zs: dict = {
    "FAZ.1": 84.7,      # top edge of fuel header
    "FAZ.2": 73.0,      # top edge of fuel elements
    "FAZ.3": 66.4025,   # top edge of active fuel elements
    "FAZ.4": 7.5975,    # bottom edge of active fuel elements
    "FAZ.5": 1.0,       # bottom edge of fuel elements
    "FAZ.6": -3.5       # bottom edge of fuel header
}


lattice_unit_names: dict[str:str] = {
    '8': '8-tube FA',
    '6': '6-tube FA',
    '4': '4-tube FA',
    # 'O': '6-tube FA with a fully withdrawn control rod',
    # 'X': '6-tube FA with a fully inserted control rod',
    # 'C': '6-tube FA with control rod',
}

lattice_unit_boundaries: list[str] = [
    'reflective',  # Reflective
    'water'        # Surrounded by water
]


class IRT4M:
    """ Class that returns IRT4M fuel units """
    def __init__(self, material: VR1Material, fa_type: str, boundary: str) -> None:
        if boundary not in lattice_unit_boundaries:
            raise ValueError(f'boundary {boundary} is not valid')
        self.boundary: str = boundary
        self.known_fuel_assemblies: list[str] = list(lattice_unit_names.keys())
        if fa_type not in self.known_fuel_assemblies:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type: str = fa_type
        self.material = material
        self.surfaces: dict = {}
        self.cells: dict = {}

    def name(self) -> str:
        """ Returns the name of the FA lattice """
        return lattice_unit_names[self.fa_type]

    def build(self) -> openmc.Universe:
        """ Builds an IRT4M fuel assembly lattice until. TODO: control rod lattices
        """
        n_plates: int = int(lattice_unit_names[self.fa_type][0])  # How many plates in the FA
        """ FA surfaces """
        self.surfaces['boundary_XY'] = openmc.model.RectangularPrism(width=lattice_wh, height=lattice_wh)
        for plane, z in plane_zs.items():
            self.surfaces[plane] = openmc.ZPlane(z0=z)
        if self.boundary == 'reflective':
            self.surfaces['boundary_XY'].boundary_type = 'reflective'
            self.surfaces['FAZ2'].boundary_type = 'reflective'  # TODO - change to FAZ 1 an 6
            self.surfaces['FAZ6'].boundary_type = 'reflective'  # once these are implemented.
        for sqc, v in rounded_rectangles.items():
            if int(sqc[0]) <= n_plates:
                self.surfaces[sqc] = openmc.model.RectangularPrism(width=sqc['wh'], height=sqc['wh'], corner_radius=sqc['corner_r'])
        if n_plates == 8:
            for cylz, r in cyl_zs.items():
                self.surfaces[cylz] = openmc.ZCylinder(r=r)

        """ Common FA cells """
        self.cells['out_top_c'] = openmc.Cell(fill=self.material.water, region=-self.surfaces['boundary_XY'] & +self.surfaces['1FT1'] & -self.surfaces['FAZ2'] & +self.surfaces['FAZ3'])
        self.cells['out_mid_f'] = openmc.Cell(fill=self.material.water, region=-self.surfaces['boundary_XY'] & +self.surfaces['1FT1'] & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
        self.cells['out_bot_c'] = openmc.Cell(fill=self.material.water, region=-self.surfaces['boundary_XY'] & +self.surfaces['1FT1'] & -self.surfaces['FAZ4'] & +self.surfaces['FAZ5'])

        for i in range(1, n_plates-1):
            self.cells[f'top_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ2'] & +self.surfaces['FAZ3'])
            self.cells[f'top_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4'] & +self.surfaces[f'{i+1}FT1'] & -self.surfaces['FAZ2'] & +self.surfaces['FAZ3'])

            self.cells[f'mid_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT2']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
            self.cells[f'mid_f_{i}'] = openmc.Cell(fill=self.material.fuel,     region=-self.surfaces[f'{i}FT2'] & +self.surfaces[f'{i}FT3']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
            self.cells[f'mid_w_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT3'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
            self.cells[f'mid_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4'] & +self.surfaces[f'{i+1}FT1'] & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])

            self.cells[f'bot_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ4'] & +self.surfaces['FAZ5'])
            self.cells[f'bot_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4'] & +self.surfaces[f'{i+1}FT1'] & -self.surfaces['FAZ4'] & +self.surfaces['FAZ5'])

        i = n_plates
        self.cells[f'top_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ2'] & +self.surfaces['FAZ3'])
        self.cells[f'top_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4']                               & -self.surfaces['FAZ2'] & +self.surfaces['FAZ3'])

        self.cells[f'mid_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT2']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
        self.cells[f'mid_f_{i}'] = openmc.Cell(fill=self.material.fuel,     region=-self.surfaces[f'{i}FT2'] & +self.surfaces[f'{i}FT3']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
        self.cells[f'mid_w_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT3'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])
        self.cells[f'mid_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4'] &                               -self.surfaces['FAZ3'] & +self.surfaces['FAZ4'])

        self.cells[f'bot_c_{i}'] = openmc.Cell(fill=self.material.cladding, region=-self.surfaces[f'{i}FT1'] & +self.surfaces[f'{i}FT4']   & -self.surfaces['FAZ4'] & +self.surfaces['FAZ5'])
        self.cells[f'bot_w_{i}'] = openmc.Cell(fill=self.material.water,    region=-self.surfaces[f'{i}FT4']                               & -self.surfaces['FAZ4'] & +self.surfaces['FAZ5'])

        return openmc.Universe(self.cells)
