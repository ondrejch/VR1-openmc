""" General OpenMC settings """

import os
from datetime import datetime
MY_TIME_NOW: str = datetime.isoformat(datetime.now(), "#", "seconds")


class SettingsOpenMC:
    """
    SettingsOpenMC class is designed to initialize and manage various simulation parameters for an OpenMC nuclear simulation.
    Parameters:
        - name (str): The name of the simulation; defaults to 'openmc deck'.
        - xs_lib (str): The cross-section library to use, either 'endf7.1' or 'endf8.0'; defaults to 'endf7.1'.
        - xs_xml_root_path (str): The root path for cross-section XML files; defaults to '/opt/OpenMC_DATA'.
        - tallies (list, None): A list of tallies to use in the simulation, if applicable.
        - plots (list, None): A list of plots to generate, if applicable.
        - parm (dict, None): Simulation parameters such as number of particles and generations.
        - rotation (float): The rotation angle for the simulation setup; defaults to 0.0.
        - sources (None, list): A list of source terms for the simulation.
        - power (None, float): The power level in Watts for thermal simulations.
    Processing Logic:
        - Sets the cross-section XML path based on the chosen library.
        - Initializes default particle generation parameters if none are provided.
        - Retrieves the current host name for record keeping.
        - Checks and enforces valid cross-section library choice.
    """
    def __init__(self, name: str = 'openmc deck', xs_lib: str = 'endf7.1', xs_xml_root_path: str = '/opt/OpenMC_DATA',
                 tallies: (list, None) = None, plots: (list, None) = None, parm: (dict, None) = None,
                 rotation: float = 0.0, sources: (None, list) = None, power: (None, float) = None):
        """Initializes an instance with various simulation parameters for the OpenMC nuclear simulation.
        Parameters:
            - name (str): The name of the simulation; defaults to 'openmc deck'.
            - xs_lib (str): The cross-section library to use, either 'endf7.1' or 'endf8.0'; defaults to 'endf7.1'.
            - xs_xml_root_path (str): The root path for cross-section XML files; defaults to '/opt/OpenMC_DATA'.
            - tallies (list, None): A list of tallies to use in the simulation, if applicable.
            - plots (list, None): A list of plots to generate, if applicable.
            - parm (dict, None): Simulation parameters such as the number of particles and generations.
            - rotation (float): The rotation angle for the simulation setup; defaults to 0.0.
            - sources (None, list): A list of source terms for the simulation.
            - power (None, float): The power level in Watts for thermal simulations.
        Returns:
            - None: This is an initializer function and does not return a value."""
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

