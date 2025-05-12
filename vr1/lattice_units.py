import openmc
from materials import VR1Material

lattice_wh: float = 9.5

rounded_rectangles: dict = {
    "1FT.1": {"wh": 6.964, "corner_r": 0.932},
    "1FT.2": {"wh": 6.87, "corner_r": 0.885},
    "1FT.3": {"wh": 6.73, "corner_r": 0.815},
    "1FT.4": {"wh": 6.636, "corner_r": 0.768},
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
    "8FT.1": 1.067,
    "8FT.2": 1.02,
    "8FT.3": 0.95,
    "8FT.4": 0.903,
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


lattice_unit_names: dict = {
    '8': '8-tube FA',
    '6': '6-tube FA',
    'C': '6-tube FA with control rod',
    '4': '4-tube FA'
}


class IRT4M:
    """ Class that returns IRT4M fuel units """
    def __init__(self, material: VR1Material):
        self.material = material
        self.known_fuel_assemblies: list[str] = ['8', '6', 'C', '4']
        self.surfaces: dict = {}
        self.fa_type: str = ''

    def name(self):
        return lattice_unit_names[self.fa_type]

    def lattice(self, fa_type: str):
        if fa_type in self.known_fuel_assemblies:
            raise ValueError(f'{fa_type} is not a known fuel assembly type!')
        self.fa_type = fa_type
        """ Common FA surfaces """
        self.surfaces['boundaryXY'] = openmc.model.RectangularPrism(width=lattice_wh, height=lattice_wh)
        for plane, z in plane_zs.items():
            self.surfaces[plane] = openmc.ZPlane(z0=z)
        for sqc, v in rounded_rectangles.items():
            self.surfaces[sqc] = openmc.model.RectangularPrism(width=sqc['wh'], height=sqc['wh'],
                                                               corner_radius=sqc['corner_r'])


cell_0819 = openmc.Cell(fill=cladding, region=-surf_6FT1 & +surf_6FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0820 = openmc.Cell(fill=water, region=-surf_6FT4 & +surf_7FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0821 = openmc.Cell(fill=cladding, region=-surf_7FT1 & +surf_7FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0822 = openmc.Cell(fill=water, region=-surf_7FT4 & +surf_8FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0823 = openmc.Cell(fill=cladding, region=-surf_8FT1 & +surf_8FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0824 = openmc.Cell(fill=water, region=-surf_8FT4 & -surf_FAZ2 & +surf_FAZ3)


