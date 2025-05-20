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
radial_channel_dict = fuel_dummy_dict
bottom_nozzle_dict  = fuel_dummy_dict
small_channel_dict  = fuel_dummy_dict
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
vessel_dict = {"Fe54": 3.734050e-02, "Fe54": 5.861660e-01, "Fe57": 1.353710e-02, "Fe58": 1.801540e-03, 
               "C12": 3.501192E-02, "C13": 3.786794E-04, "Si28": 1.395870e-02, "Si29": 7.087880e-04,
               "Si30": 4.672390e-04, "Mn55": 1.934300e-03, "P31": 6.003990e-04, "S32": 3.146070e-04,
               "S33": 2.518710e-06, "S34": 1.421750e-05, "S36": 6.628190e-08, "Cr50": 7.992040e-03,
               "Cr52": 1.541190e-01, "Cr53": 1.747580e-02, "Cr54": 4.350100e-03, "Ni58":6.162780e-02,
               "Ni60": 2.373890e-02, "Ni61": 1.031910e-03, "Ni62": 3.290190e-03, "Ni64": 8.379150e-04,
               "Ti46": 2.747290e-03, "Ti47": 2.477560e-03, "Ti48": 2.454910e-02, "Ti49": 1.801560e-03,
               "Ti50": 1.724970e-03}
abs_tube_dict = vessel_dict
damper_dict = vessel_dict
cd_layer_dict = {"Cd106": 1.250000e-02, "Cd108": 8.900000e-03, "Cd110": 1.249000e-01, "Cd111": 1.280000e-01,
                 "Cd112": 2.413000e-01, "Cd113": 1.222000e-01, "Cd114": 2.873000e-01, "Cd116": 7.490000e-02}
abs_head_dict = {"C12": 0.613229215, "C13": 0.007187085, "Al27": 22.34264, "Si28": 0.5699801, "Si29": 0.02997625,
                 "Si30": 0.02044071, "P31": 0.02714242, "S32": 0.06318908, "S33": 0.0005217, "S34": 0.003033851,
                 "S36": 1.497626e-05, "Ti46": 0.1842596, "Ti47": 0.1697818, "Ti48": 1.717988, "Ti49": 0.1287059,
                 "Ti50": 0.1257434, "Cr50": 0.5826037, "Cr52": 11.68361, "Cr53": 1.350332, "Cr54": 0.3424647,
                 "Mn55": 0.1551, "Fe54": 2.94223, "Fe56": 47.89526, "Fe57": 1.125895, "Fe58": 0.152462,
                 "Ni58": 5.211166, "Ni60": 2.076471, "Ni61": 0.09176879, "Ni62": 0.2973895, "Ni64": 0.07818203,
                 "Cu63": 0.003843418, "Cu65": 0.001767457, "Zn64": 2.726370e-03, "Zn66": 1.565140e-03,
                 "Zn67": 2.300020e-04, "Zn68": 1.054640e-03, "Zn70": 3.365880e-05}
air_dict = {"N14": 0.7551, "O16": 0.2449}

# TODO - add more materials from the serpent deck

#
# class Singleton:
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


class VR1Materials:
    """ Materials used in the model. TODO: graphite, air, control rod materials """

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

        self.air = openmc.Material(name='air')
        self.air.add_components(air_dict,'wo')
        self.air.set_density('g/cm3',0.001161)
        self.air.temperature=293.15

        self.cladding = openmc.Material(name='fuel cladding')
        self.cladding.add_components(cladding_dict, 'wo')
        self.cladding.set_density('g/cm3', 2.7)
        self.cladding.temperature = 293.15

        self.guidetube = openmc.Material(name='guidetube')
        self.guidetube.add_components(guid_tube_dict,'wo')
        self.guidetube.set_density('g/cm3',2.7)
        self.guidetube.temperature = 293.15

        self.vessel = openmc.Material(name='vessel')
        self.vessel.add_components(vessel_dict,'ao')
        self.vessel.set_density('g/cm3',7.85)
        self.vessel.temperature = 293.15

        self.abstube = openmc.Material(name='abstube')
        self.abstube.add_components(abs_tube_dict,'ao')
        self.abstube.set_density('g/cm3',7.85)
        self.abstube.temperature = 293.15

        self.damper = openmc.Material(name='damper')
        self.damper.add_components(damper_dict,'ao')
        self.damper.set_density('g/cm3',7.85)
        self.damper.temperature = 293.15

        self.radialchannel = openmc.Material(name='radialchannel')
        self.radialchannel.add_components(radial_channel_dict,'wo')
        self.radialchannel.set_density('g/cm3',2.65)
        self.radialchannel.temperature = 293.15

        self.cdlayer = openmc.Material(name='cdlayer')
        self.cdlayer.add_components(cd_layer_dict,'ao')
        self.cdlayer.set_density('g/cm3',8.65)
        self.cdlayer.temperature = 293.15

        self.abshead = openmc.Material(name='abshead')
        self.abshead.add_components(abs_head_dict,'wo')
        self.abshead.set_density('g/cm3',5.497)
        self.abshead.temperature = 293.15

        self.abscenter = openmc.Material(name='abscenter')
        self.abscenter.add_components(abs_center_dict,'wo')
        self.abscenter.set_density('g/cm3',2.7)
        self.abscenter.temperature=293.15

        self.dummy = openmc.Material(name='fuel dummy')
        self.dummy.add_components(cladding_dict, 'wo')
        self.dummy.set_density('g/cm3', 2.65)
        self.dummy.temperature = 293.15

    def get_materials(self):
        return openmc.Materials([self.fuel, self.water, self.cladding, self.dummy])
