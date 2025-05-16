""" General OpenMC settings """

import os
from datetime import datetime
MY_TIME_NOW: str = datetime.isoformat(datetime.now(), "#", "seconds")


class SettingsOpenMC:
    def __init__(self, name: str = 'openmc deck', xs_lib: str = 'endf7.1', xs_xml_root_path: str = '/opt/OpenMC_DATA',
                 tallies: (list, None) = None, plots: (list, None) = None, parm: (dict, None) = None,
                 rotation: float = 0.0, sources: (None, list) = None, power: (None, float) = None):
        self.supported_code: str = "OpenMC"
        self.name = name
        self.my_time_now = MY_TIME_NOW
        self.xs_lib = xs_lib
        self.xs_xml_root_path = xs_xml_root_path
        if xs_lib == 'endf7.1':
            self.xs_xml: str = os.path.join(xs_xml_root_path, 'endfb-vii.1-hdf5/cross_sections2.xml')
        elif xs_lib == 'endf8.0':
            self.xs_xml: str = os.path.join(xs_xml_root_path, 'endfb-viii.0-hdf5/cross_sections.xml')
        else:
            assert ValueError('xs_lib must be endf8.0 or endf7.1')
        self.hostname = os.uname()[1]
        self.power = power  # [W_th]
        self.tallies = tallies
        self.plots = plots
        self.sources = sources
        self.rotation = rotation

        self.generations_per_batch: int = 1
        if parm is None:
            """ npg: Number of particles per generation
                gen: Number of generations
                nsk: Number of skipped generations """
            self.parm = {'npg': 1000, 'gen': 110, 'nsk': 10}
        else:
            self.parm = parm
