""" Materials used in VR1 """

import openmc

fuel_dict = {'U235': 0.09976, 'U238': 0.40724, 'O16': 0.06832, 'Al27': 0.42467}
water_dict = {'H': 2, 'O': 1}
cladding_dict = {'Al27': 0.9807392, 'Mg24': 0.005259756, 'Mg25': 0.00069362, 'Mg26': 0.000794222, 'Si28': 0.008728932,
    'Si29': 0.000459064, 'Si30': 0.000313054, 'Fe54': 0.000113003, 'Fe56': 0.001845614, 'Fe57': 4.48842E-05,
    'Fe58': 6.88202E-06, 'Cu63': 0.000684552, 'Cu65': 0.000315983, 'B10': 2.19563E-07, 'B11': 9.78493E-07}
fuel_dummy_dict = {"Al27": 0.9582268, "Mn55": 0.003000477, "Mg24": 0.0249354, "Mg25": 0.003288316, "Mg26": 0.003765249,
    "Cu63": 0.000342546, "Cu65": 0.000157524, "Fe54": 0.000112928, "Fe56": 0.001838391, "Fe57": 4.32147e-05,
    "Fe58": 5.85197e-06, "S32": 0.002161128, "S33": 1.78425e-05, "S34": 0.000103768, "S36": 5.12223e-07,
    "Ti46": 7.92054e-05, "Ti47": 7.29817e-05, "Ti48": 0.000738532, "Ti49": 5.5327e-05, "Ti50": 5.40558e-05,
    "Zn64": 0.000485975, "Zn66": 0.000278985, "Zn67": 4.09979e-05, "Zn68": 0.00018799, "Zn70": 5.99969e-06}
abs_center_dict = {"Al27": 0.9952163, "Cu63": 0.000171273, "Cu65": 7.87622e-05, "Fe54": 0.000112928, "Fe56": 0.00183839,
    "Fe57": 4.32146e-05, "Fe58": 5.85197e-06, "S32": 0.002161122, "S33": 1.78424e-05, "S34": 0.000103768,
    "S36": 5.12223e-07, "Zn64": 0.000121493, "Zn66": 6.97462e-05, "Zn67": 1.02494e-05, "Zn68": 4.69974e-05,
    "Zn70": 1.49992e-06}
guid_tube_dict = abs_center_dict
rabbit_tube_dict = abs_center_dict
grid_dict = {"Al27": 0.9353353, "Mn55": 0.002999189, "Mg24": 0.03894506, "Mg25": 0.005135806, "Mg26": 0.005880707,
    "Cr50": 4.17238e-05, "Cr52": 0.000836786, "Cr53": 9.67094e-05, "Cr54": 2.45272e-05, "Cu63": 0.0006848,
    "Cu65": 0.000314914, "Fe54": 0.00011288, "Fe56": 0.00183761, "Fe57": 4.31962e-05, "Fe58": 5.84949e-06,
    "S32": 0.005400523, "S33": 4.45872e-05, "S34": 0.00025931, "S36": 1.28002e-06, "Zn64": 0.000485768,
    "Zn66": 0.000278866, "Zn67": 4.09805e-05, "Zn68": 0.00018791, "Zn70": 5.99714e-06, "Ti46": 7.91718e-05,
    "Ti47": 7.29506e-05, "Ti48": 0.000738218, "Ti49": 5.53035e-05, "Ti50": 5.4033e-05, }
big_channel_dict = grid_dict
# TODO - add more materials from the serpent deck
abs_tube_dict = {}


class VR1Materials:
    """ Materials used in the model. TODO: graphite, air, control rod materials """
    # def __new__(cls):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(VR1Materials, cls).__new__(cls)
    #     return cls.instance
    # NOTE: Singleton does not help, it has to be the same identical instance or OpenMC's internal numbering breaks.
    # This is why I create vr1_materials below, and use it though out the code.
    def __init__(self, *args, **kwargs):
        self.fuel = openmc.Material(name='fuel meat')
        self.fuel.add_components(fuel_dict, 'wo')
        self.fuel.set_density('g/cm3', 5.53)
        self.fuel.temperature = 293.15
        self.fuel.depletable = True

        self.water = openmc.Material(name='water in the pool')
        self.water.add_components(water_dict, 'ao')
        self.water.set_density('g/cm3', 0.9982)
        self.water.temperature = 293.15
        self.water.add_s_alpha_beta('c_H_in_H2O')

        self.cladding = openmc.Material(name='fuel cladding')
        self.cladding.add_components(cladding_dict, 'wo')
        self.cladding.set_density('g/cm3', 2.7)
        self.cladding.temperature = 293.15

        self.dummy = openmc.Material(name='fuel dummy')
        self.dummy.add_components(cladding_dict, 'wo')
        self.dummy.set_density('g/cm3', 2.65)
        self.dummy.temperature = 293.15

    def get_materials(self):
        return openmc.Materials([self.fuel, self.water, self.cladding, self.dummy])


vr1_materials = VR1Materials()  # Use only this instance
