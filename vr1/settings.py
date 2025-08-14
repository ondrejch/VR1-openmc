""" General OpenMC settings """

import os
import openmc
from datetime import datetime

MY_TIME_NOW: str = datetime.isoformat(datetime.now(), "#", "seconds")

class SettingsOpenMC:
    def __init__(self,
                 name: str = 'openmc deck',
                 xs_lib: str = 'endf7.1',
                 xs_xml_root_path: str = '/opt/OpenMC_DATA',
                 tallies: (list, None) = None,
                 plots: (list, None) = None,
                 parm: (dict, None) = None,
                 rotation: float = 0.0,
                 sources: (None, list) = None,
                 power: (None, float) = None
        ):

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

    def create_source(self, source_lower_left, source_upper_right, source_type='uniform'):
        """
        Create an OpenMC source definition for arbitrary lattice configuration
        
        Parameters:
        - source_lower_left: [x, y, z] lower left corner of source region
        - source_upper_right: [x, y, z] upper right corner of source region  
        - source_type: Type of source distribution ('uniform', 'point')
        """
        source = openmc.Source()
        
        if source_type == 'uniform':
            # Create uniform source over the specified region
            source.space = openmc.stats.Box(
                lower_left=source_lower_left,
                upper_right=source_upper_right
            )
        elif source_type == 'point':
            # Point source at center of region
            center = [
                (source_lower_left[0] + source_upper_right[0]) / 2,
                (source_lower_left[1] + source_upper_right[1]) / 2,
                (source_lower_left[2] + source_upper_right[2]) / 2
            ]
            source.space = openmc.stats.Point(center)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
            
        # Default energy and angle distributions
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Watt(a=0.988e6, b=2.249e-6)  # U-235 fission spectrum
        
        if self.sources is None:
            self.sources = []
        self.sources.append(source)
        
        return source

    def create_settings_xml(self, geometry=None, materials=None, output_path='.'):
        """
        Create settings.xml file for OpenMC simulation
        
        Parameters:
        - geometry: OpenMC geometry object
        - materials: OpenMC materials object
        - output_path: Directory to write settings.xml
        """
        settings = openmc.Settings()
        
        # Basic settings
        settings.particles = self.parm['npg']
        settings.generations_per_batch = self.generations_per_batch
        settings.batches = self.parm['gen']
        settings.inactive = self.parm['nsk']
        
        # Cross sections
        settings.cross_sections = self.xs_xml
        
        # Sources
        if self.sources:
            settings.source = self.sources
        
        # Temperature handling
        settings.temperature = {'default': 293.15, 'method': 'interpolation'}
        
        # Export settings
        settings_file = os.path.join(output_path, 'settings.xml')
        settings.export_to_xml(settings_file)
        
        print(f"Settings XML exported to: {settings_file}")
        return settings_file