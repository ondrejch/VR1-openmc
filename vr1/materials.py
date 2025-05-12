import openmc

fuel_dict = {'U235': 0.09976,
             'U238': 0.40724,
             'O16': 0.06832,
             'Al27': 0.42467}

water_dict = {'H': 2, 'O': 1}

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


class VR1Material(object):
    def __init__(self):
        self.fuel = openmc.Material(name='fuel')
        self.fuel.add_components(fuel_dict, 'wo')
        self.fuel.set_density('g/cm3', 5.53)
        self.fuel.temperature = 293.15
        self.fuel.depletable = True

        self.water = openmc.Material(name='water')
        self.water.add_components(water_dict, 'ao')
        self.water.set_density('g/cm3', 0.9982)
        self.water.temperature = 293.15
        self.water.add_s_alpha_beta('c_H_in_H2O')

        self.cladding = openmc.Material(name='cladding')
        self.cladding.add_components(cladding_dict, 'wo')
        self.cladding.set_density('g/cm3', 2.7)
        self.cladding.temperature = 293.15

    def get_materials(self):
        return openmc.Materials([self.fuel, self.water, self.cladding])

