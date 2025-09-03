"""
python ./ESAR.py | awk ' /RectangularPrism/ {print "\""$1"\": {\"wh\": "$3", \"corner_r\": "$6" },"}'
python ./ESAR.py | awk ' /cylz/ {print "\""$1"\": "$3}'
"""

#%matplotlib inline
from numbers import Real

import openmc
import openmc.deplete
import matplotlib.pyplot as plt
import numpy as np

# openmc.Materials.cross_sections = ""
chain_file = ""


class srp_to_omc(object):
    def __init__(self, raw_str):
        self.surface = None
        split_str = raw_str.split(' ')
        self.id = split_str[1]
        self.surf_type = split_str[2]
        self.params = split_str[2:]
        if '%' in self.params:
            self.params = self.params[:self.params.index('%')]

    def omc_surface(self):
        srp_to_omc_types = {'sqc': srp_to_omc.sqc,
                            'pz': srp_to_omc.plane,
                            'py': srp_to_omc.plane,
                            'px': srp_to_omc.plane,
                            'cylz': srp_to_omc.cyl,
                            'cyly': srp_to_omc.cyl,
                            'cylx': srp_to_omc.cyl,
                            'ckz': srp_to_omc.cone,
                            'cky': srp_to_omc.cone,
                            'ckx': srp_to_omc.cone, }
        print(f'{self.id} ',end='')
        self.surface = srp_to_omc_types[self.surf_type](self.params).build()
        return self.surface

    class sqc(object):
        #   "surf 1FT.1 sqc 0 0 3.482 0.932 % 1st tube outer cladding"
        #               x0 y0 r  corner_r
        def __init__(self, params):
            params += [1E3]
            # assert len(params) == 6, "OpenMC does not have the ability to make an infinite square prism.\nYou're going to need to specify its total height as the final parameter, or you're going to need to just manually create this one."
            self.r, self.coords = float(params[3]), [float(params[1]), float(params[2])]
            # self.corner_r, self.height =  float(params[4]),float(params[5])
            self.corner_r = float(params[4])

        def build(self):
            print(f'RectangularPrism  {self.r * 2} {self.coords} {self.corner_r}')
            return openmc.model.RectangularPrism(width=self.r * 2, height=self.r * 2, origin=self.coords,
                                                 corner_radius=self.corner_r)

    class rect(object):
        def __init__(self, params):
            self.width, self.height = (float(params[1]) - float(params[2])), (float(params[3]) - float(params[4]))
            self.coords = [(float(params[1]) - float(params[2])) / 2, (float(params[3]) - float(params[4])) / 2]

        def build(self):
            print(f'RectangularPrism  {self.width} {self.height} {self.coords}')
            return openmc.model.RectangularPrism(width=self.width, height=self.height, origin=self.coords)

    class plane(object):
        #   surf FAZ.1 pz 84.7 % top edge of fuel header

        def __init__(self, params):
            self.plane_type, self.loc = params
            self.surface = self.build()

        def build(self):
            print(f'{self.plane_type} {self.loc}')
            if self.plane_type == 'pz':
                return openmc.ZPlane(z0=float(self.loc))

            if self.plane_type == 'py':
                return openmc.YPlane(y0=float(self.loc))

            if self.plane_type == 'px':
                return openmc.XPlane(x0=float(self.loc))

    class cyl(object):
        #surf 8FT.1 cylz 0 0 1.067 % 8th tube outer cladding
        """
        params: [cyl_type, 2d coord 1, 2d coord 2, radius, bottom lim (OPTIONAL), top lim (OPTIONAL)]
        """

        def __init__(self, params):
            # print(params)
            if len(params) == 4:
                self.cyl_type = params[0]
                self.r, self.coords = float(params[3]), [float(params[1]), float(params[2])]

        def build(self):
            print(f'{self.cyl_type} {self.r} {self.coords}')
            if self.cyl_type == 'cylz':
                return openmc.ZCylinder(r=self.r, x0=self.coords[0], y0=self.coords[1])

            if self.cyl_type == 'cyly':
                return openmc.YCylinder(r=self.r, x0=self.coords[0], z0=self.coords[1])

            if self.cyl_type == 'cylx':
                return openmc.XCylinder(r=self.r, y0=self.coords[0], z0=self.coords[1])

    class cone(object):
        def __init__(self, params):
            #surf RCky.1 cky 0 -103.5 35.3 0.1162 -1 % cone of the lead shielding
            self.cone_type = params[0]
            self.coords = float(params[1]), float(params[2]), float(params[3])
            self.r2, self.up = float(params[4]), int(params[5])

        def build(self):
            print(f'{self.cone_type} {self.coords}')
            if self.cone_type == 'ckz':
                return openmc.model.ZConeOneSided(x0=self.coords[0], y0=self.coords[1], z0=self.coords[2], r2=self.r2,
                                                  up=self.up)

            if self.cone_type == 'cky':
                return openmc.model.YConeOneSided(x0=self.coords[0], y0=self.coords[1], z0=self.coords[2], r2=self.r2,
                                                  up=self.up)

            if self.cone_type == 'ckx':
                return openmc.model.XConeOneSided(x0=self.coords[0], y0=self.coords[1], z0=self.coords[2], r2=self.r2,
                                                  up=self.up)


fuel = openmc.Material()
fuel_dict = {'U235': 0.09976,
             'U238': 0.40724,
             'O16': 0.06832,
             'Al27': 0.42467}
fuel.add_components(fuel_dict, 'wo')
fuel.set_density('g/cm3', 5.53)
fuel.temperature = 293.15
fuel.depletable = True

water = openmc.Material()
water_dict = {'H': 2, 'O': 1}
water.add_components(water_dict, 'ao')
water.set_density('g/cm3', 0.9982)
water.temperature = 293.15
water.add_s_alpha_beta('c_H_in_H2O')

cladding = openmc.Material()
cladding_dict = {'Al27': 0.9807392,
                 'Mg24': 0.005259756,
                 'Mg25': 0.00069362,
                 'Mg26': 0.000794222,
                 'Si28': 0.008728932,
                 'Si29': 0.000459064,
                 'Si30': 0.000313054,
                 'Fe54': 0.000113003,
                 'Fe56': 0.001845614,
                 'Fe57': 4.48842E-05,
                 'Fe58': 6.88202E-06,
                 'Cu63': 0.000684552,
                 'Cu65': 0.000315983,
                 'B10': 2.19563E-07,
                 'B11': 9.78493E-07}
cladding.add_components(cladding_dict, 'wo')
cladding.set_density('g/cm3', 2.7)
cladding.temperature = 293

materials = openmc.Materials([fuel, water, cladding])
# materials.export_to_xml()

boundary_surface = openmc.model.RectangularPrism(width=9.5, height=9.5, origin=[0, 0], corner_radius=0,
                                                 boundary_type='reflective')

surf_1FT1 = srp_to_omc('surf 1FT.1 sqc 0 0 3.482 0.932 % 1st tube outer cladding').omc_surface()
surf_1FT2 = srp_to_omc('surf 1FT.2 sqc 0 0 3.435 0.885 % 1st tube outer fuel').omc_surface()
surf_1FT3 = srp_to_omc('surf 1FT.3 sqc 0 0 3.365 0.815 % 1st tube inner fuel').omc_surface()
surf_1FT4 = srp_to_omc('surf 1FT.4 sqc 0 0 3.318 0.768 % 1st tube inner cladding').omc_surface()

surf_2FT1 = srp_to_omc('surf 2FT.1 sqc 0 0 3.137 0.852 % 2nd tube outer cladding').omc_surface()
surf_2FT2 = srp_to_omc('surf 2FT.2 sqc 0 0 3.090 0.805 % 2nd tube outer fuel').omc_surface()
surf_2FT3 = srp_to_omc('surf 2FT.3 sqc 0 0 3.020 0.735 % 2nd tube inner fuel').omc_surface()
surf_2FT4 = srp_to_omc('surf 2FT.4 sqc 0 0 2.973 0.688 % 2nd tube inner cladding').omc_surface()

surf_3FT1 = srp_to_omc('surf 3FT.1 sqc 0 0 2.792 0.772 % 3rd tube outer cladding').omc_surface()
surf_3FT2 = srp_to_omc('surf 3FT.2 sqc 0 0 2.745 0.725 % 3rd tube outer fuel').omc_surface()
surf_3FT3 = srp_to_omc('surf 3FT.3 sqc 0 0 2.675 0.655 % 3rd tube inner fuel').omc_surface()
surf_3FT4 = srp_to_omc('surf 3FT.4 sqc 0 0 2.628 0.608 % 3rd tube inner cladding').omc_surface()

surf_4FT1 = srp_to_omc('surf 4FT.1 sqc 0 0 2.447 0.692 % 4th tube outer cladding').omc_surface()
surf_4FT2 = srp_to_omc('surf 4FT.2 sqc 0 0 2.400 0.645 % 4th tube outer fuel').omc_surface()
surf_4FT3 = srp_to_omc('surf 4FT.3 sqc 0 0 2.330 0.575 % 4th tube inner fuel').omc_surface()
surf_4FT4 = srp_to_omc('surf 4FT.4 sqc 0 0 2.283 0.528 % 4th tube inner cladding').omc_surface()

surf_5FT1 = srp_to_omc('surf 5FT.1 sqc 0 0 2.102 0.612 % 5th tube outer cladding').omc_surface()
surf_5FT2 = srp_to_omc('surf 5FT.2 sqc 0 0 2.055 0.565 % 5th tube outer fuel').omc_surface()
surf_5FT3 = srp_to_omc('surf 5FT.3 sqc 0 0 1.985 0.495 % 5th tube inner fuel').omc_surface()
surf_5FT4 = srp_to_omc('surf 5FT.4 sqc 0 0 1.938 0.448 % 5th tube inner cladding').omc_surface()

surf_6FT1 = srp_to_omc('surf 6FT.1 sqc 0 0 1.757 0.532 % 6th tube outer cladding').omc_surface()
surf_6FT2 = srp_to_omc('surf 6FT.2 sqc 0 0 1.710 0.485 % 6th tube outer fuel').omc_surface()
surf_6FT3 = srp_to_omc('surf 6FT.3 sqc 0 0 1.640 0.415 % 6th tube inner fuel').omc_surface()
surf_6FT4 = srp_to_omc('surf 6FT.4 sqc 0 0 1.593 0.368 % 6th tube inner cladding').omc_surface()

surf_7FT1 = srp_to_omc('surf 7FT.1 sqc 0 0 1.412 0.452 % 7th tube outer cladding').omc_surface()
surf_7FT2 = srp_to_omc('surf 7FT.2 sqc 0 0 1.365 0.405 % 7th tube outer fuel').omc_surface()
surf_7FT3 = srp_to_omc('surf 7FT.3 sqc 0 0 1.295 0.335 % 7th tube inner fuel').omc_surface()
surf_7FT4 = srp_to_omc('surf 7FT.4 sqc 0 0 1.248 0.288 % 7th tube inner cladding').omc_surface()

surf_8FT1 = srp_to_omc('surf 8FT.1 cylz 0 0 1.067 % 8th tube outer cladding').omc_surface()
surf_8FT2 = srp_to_omc('surf 8FT.2 cylz 0 0 1.020 % 8th tube outer fuel').omc_surface()
surf_8FT3 = srp_to_omc('surf 8FT.3 cylz 0 0 0.950 % 8th tube inner fuel').omc_surface()
surf_8FT4 = srp_to_omc('surf 8FT.4 cylz 0 0 0.903 % 8th tube inner cladding').omc_surface()

surf_FAZ1 = srp_to_omc('surf FAZ.1 pz 84.7 % top edge of fuel header').omc_surface()
surf_FAZ2 = openmc.ZPlane(z0=73, boundary_type='vacuum')
# surf_FAZ2 = srp_to_omc('surf FAZ.2 pz 73.0000 % top edge of fuel elements').omc_surface()
surf_FAZ3 = srp_to_omc('surf FAZ.3 pz 66.4025 % top edge of active fuel elements').omc_surface()
surf_FAZ4 = srp_to_omc('surf FAZ.4 pz 7.5975 % bottom edge of active fuel elements').omc_surface()
# surf_FAZ5 = srp_to_omc('surf FAZ.5 pz 1.0 % bottom edge of fuel elements').omc_surface()
surf_FAZ5 = openmc.ZPlane(z0=1, boundary_type='vacuum')
surf_FAZ6 = srp_to_omc('surf FAZ.6 pz -3.5 % bottom edge of fuel header').omc_surface()

cell_088 = openmc.Cell(fill=water,      region=-boundary_surface & +surf_1FT1 & -surf_FAZ2 & +surf_FAZ3)

cell_089 = openmc.Cell(fill=cladding,   region=-surf_1FT1 & +surf_1FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0810 = openmc.Cell(fill=water,     region=-surf_1FT4 & +surf_2FT1 & -surf_FAZ2 & +surf_FAZ3)

cell_0811 = openmc.Cell(fill=cladding,  region=-surf_2FT1 & +surf_2FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0812 = openmc.Cell(fill=water,     region=-surf_2FT4 & +surf_3FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0813 = openmc.Cell(fill=cladding,  region=-surf_3FT1 & +surf_3FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0814 = openmc.Cell(fill=water,     region=-surf_3FT4 & +surf_4FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0815 = openmc.Cell(fill=cladding,  region=-surf_4FT1 & +surf_4FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0816 = openmc.Cell(fill=water,     region=-surf_4FT4 & +surf_5FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0817 = openmc.Cell(fill=cladding,  region=-surf_5FT1 & +surf_5FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0818 = openmc.Cell(fill=water,     region=-surf_5FT4 & +surf_6FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0819 = openmc.Cell(fill=cladding,  region=-surf_6FT1 & +surf_6FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0820 = openmc.Cell(fill=water,     region=-surf_6FT4 & +surf_7FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0821 = openmc.Cell(fill=cladding,  region=-surf_7FT1 & +surf_7FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0822 = openmc.Cell(fill=water,     region=-surf_7FT4 & +surf_8FT1 & -surf_FAZ2 & +surf_FAZ3)
cell_0823 = openmc.Cell(fill=cladding,  region=-surf_8FT1 & +surf_8FT4 & -surf_FAZ2 & +surf_FAZ3)
cell_0824 = openmc.Cell(fill=water,     region=-surf_8FT4 & -surf_FAZ2 & +surf_FAZ3)

cell_0826 = openmc.Cell(fill=water,     region=-boundary_surface & +surf_1FT1 & -surf_FAZ3 & +surf_FAZ4)

cell_0827 = openmc.Cell(fill=cladding,  region=-surf_1FT1 & +surf_1FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0828 = openmc.Cell(fill=fuel,      region=-surf_1FT2 & +surf_1FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0829 = openmc.Cell(fill=cladding,  region=-surf_1FT3 & +surf_1FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0830 = openmc.Cell(fill=water,     region=-surf_1FT4 & +surf_2FT1 & -surf_FAZ3 & +surf_FAZ4)

cell_0831 = openmc.Cell(fill=cladding,  region=-surf_2FT1 & +surf_2FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0832 = openmc.Cell(fill=fuel,      region=-surf_2FT2 & +surf_2FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0833 = openmc.Cell(fill=cladding,  region=-surf_2FT3 & +surf_2FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0834 = openmc.Cell(fill=water,     region=-surf_2FT4 & +surf_3FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0835 = openmc.Cell(fill=cladding,  region=-surf_3FT1 & +surf_3FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0836 = openmc.Cell(fill=fuel,      region=-surf_3FT2 & +surf_3FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0837 = openmc.Cell(fill=cladding,  region=-surf_3FT3 & +surf_3FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0838 = openmc.Cell(fill=water,     region=-surf_3FT4 & +surf_4FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0839 = openmc.Cell(fill=cladding,  region=-surf_4FT1 & +surf_4FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0840 = openmc.Cell(fill=fuel,      region=-surf_4FT2 & +surf_4FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0841 = openmc.Cell(fill=cladding,  region=-surf_4FT3 & +surf_4FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0842 = openmc.Cell(fill=water,     region=-surf_4FT4 & +surf_5FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0843 = openmc.Cell(fill=cladding,  region=-surf_5FT1 & +surf_5FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0844 = openmc.Cell(fill=fuel,      region=-surf_5FT2 & +surf_5FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0845 = openmc.Cell(fill=cladding,  region=-surf_5FT3 & +surf_5FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0846 = openmc.Cell(fill=water,     region=-surf_5FT4 & +surf_6FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0847 = openmc.Cell(fill=cladding,  region=-surf_6FT1 & +surf_6FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0848 = openmc.Cell(fill=fuel,      region=-surf_6FT2 & +surf_6FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0849 = openmc.Cell(fill=cladding,  region=-surf_6FT3 & +surf_6FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0850 = openmc.Cell(fill=water,     region=-surf_6FT4 & +surf_7FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0851 = openmc.Cell(fill=cladding,  region=-surf_7FT1 & +surf_7FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0852 = openmc.Cell(fill=fuel,      region=-surf_7FT2 & +surf_7FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0853 = openmc.Cell(fill=cladding,  region=-surf_7FT3 & +surf_7FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0854 = openmc.Cell(fill=water,     region=-surf_7FT4 & +surf_8FT1 & -surf_FAZ3 & +surf_FAZ4)
cell_0855 = openmc.Cell(fill=cladding,  region=-surf_8FT1 & +surf_8FT2 & -surf_FAZ3 & +surf_FAZ4)
cell_0856 = openmc.Cell(fill=fuel,      region=-surf_8FT2 & +surf_8FT3 & -surf_FAZ3 & +surf_FAZ4)
cell_0857 = openmc.Cell(fill=cladding,  region=-surf_8FT3 & +surf_8FT4 & -surf_FAZ3 & +surf_FAZ4)
cell_0858 = openmc.Cell(fill=water,     region=-surf_8FT4 & -surf_FAZ3 & +surf_FAZ4)

cell_0860 = openmc.Cell(fill=water,     region=-boundary_surface & +surf_1FT1 & -surf_FAZ4 & +surf_FAZ5)

cell_0861 = openmc.Cell(fill=cladding,  region=-surf_1FT1 & +surf_1FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0862 = openmc.Cell(fill=water,     region=-surf_1FT4 & +surf_2FT1 & -surf_FAZ4 & +surf_FAZ5)

cell_0863 = openmc.Cell(fill=cladding,  region=-surf_2FT1 & +surf_2FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0864 = openmc.Cell(fill=water,     region=-surf_2FT4 & +surf_3FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0865 = openmc.Cell(fill=cladding,  region=-surf_3FT1 & +surf_3FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0866 = openmc.Cell(fill=water,     region=-surf_3FT4 & +surf_4FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0867 = openmc.Cell(fill=cladding,  region=-surf_4FT1 & +surf_4FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0868 = openmc.Cell(fill=water,     region=-surf_4FT4 & +surf_5FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0869 = openmc.Cell(fill=cladding,  region=-surf_5FT1 & +surf_5FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0870 = openmc.Cell(fill=water,     region=-surf_5FT4 & +surf_6FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0871 = openmc.Cell(fill=cladding,  region=-surf_6FT1 & +surf_6FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0872 = openmc.Cell(fill=water,     region=-surf_6FT4 & +surf_7FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0873 = openmc.Cell(fill=cladding,  region=-surf_7FT1 & +surf_7FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0874 = openmc.Cell(fill=water,     region=-surf_7FT4 & +surf_8FT1 & -surf_FAZ4 & +surf_FAZ5)
cell_0875 = openmc.Cell(fill=cladding,  region=-surf_8FT1 & +surf_8FT4 & -surf_FAZ4 & +surf_FAZ5)
cell_0876 = openmc.Cell(fill=water,     region=-surf_8FT4 & -surf_FAZ4 & +surf_FAZ5)

root_list = [cell_088, cell_089, cell_0810, cell_0811, cell_0812, cell_0813, cell_0814, cell_0815, cell_0816, cell_0817,
             cell_0818, cell_0819, cell_0820,
             cell_0821, cell_0822, cell_0823, cell_0824, cell_0826, cell_0827, cell_0828, cell_0829, cell_0830,
             cell_0831, cell_0832, cell_0833, cell_0834, cell_0835, cell_0836, cell_0837, cell_0838, cell_0839,
             cell_0840,
             cell_0841, cell_0842, cell_0843, cell_0844, cell_0845, cell_0846, cell_0847, cell_0848, cell_0849,
             cell_0850,
             cell_0851, cell_0852, cell_0853, cell_0854, cell_0855, cell_0856, cell_0857, cell_0858, cell_0860,
             cell_0861, cell_0862, cell_0863, cell_0864, cell_0865, cell_0866, cell_0867, cell_0868, cell_0869,
             cell_0870,
             cell_0871, cell_0872, cell_0873, cell_0874, cell_0875, cell_0876]

root_universe = openmc.Universe(cells=root_list)
test_universe = openmc.Universe(
    cells=[cell_088, cell_089, cell_0810, cell_0811, cell_0812, cell_0813, cell_0814, cell_0815, cell_0816, cell_0817,
           cell_0818, cell_0819, cell_0820])
geometry = openmc.Geometry(root=root_universe)
# geometry.export_to_xml()

settings = openmc.Settings()

settings.run_mode = 'eigenvalue'
settings.temperature = {'method': 'interpolation', 'range': (293.15, 923.15)}
settings.photo_transport = False

settings.batches = 100
settings.inactive = 25
settings.particles = 1000
source_area = openmc.stats.Box([-3.5, -3.5, 1], [3.5, 3.5, 73])
# source_area = openmc.stats.Box([-1,-1,20],[1,1,30])
settings.source = openmc.Source(space=source_area)

materials.cross_sections = '/opt/OpenMC_DATA/endfb-vii.1-hdf5/cross_sections2.xml'
openmc_model = openmc.Model()
openmc_model.materials = materials
openmc_model.geometry = geometry
openmc_model.settings = settings
# openmc_model.tallies = tallies
# openmc.config['cross_sections'] =
       # Plot the geometry
plot = openmc.Plot()
plot.filename = 'plot_xy.png'
plot.width = (10, 10)
plot.pixels = (2000, 2000)
plot.origin = (0, 0, 30)
plot.color_by = 'cell'
plot.basis = 'xy'

plotf = openmc.Plot()
plotf.filename = 'plot_xy_m.png'
plotf.width = (10, 10)
plotf.pixels = (2000, 2000)
plotf.origin = (0, 0, 30)
plotf.color_by = 'material'
plotf.basis = 'xy'

plot1 = openmc.Plot()
plot1.filename = 'plot_yz.png'
plot1.width = (10, 100)
plot1.pixels = (200, 2000)
plot1.origin = (0, 0, 30)
plot1.color_by = 'cell'
plot1.basis = 'yz'

plot1f = openmc.Plot()
plot1f.filename = 'plot_yz_m.png'
plot1f.width = (10, 100)
plot1f.pixels = (200, 2000)
plot1f.origin = (0, 0, 30)
plot1f.color_by = 'material'
plot1f.basis = 'yz'

openmc_model.plots = openmc.Plots([plot, plotf, plot1, plot1f])
# openmc_model.plot_geometry()

openmc_model.export_to_model_xml()
# settings.export_to_xml()

# openmc.run()
