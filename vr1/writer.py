""" OpenMC model writer for VR1 """

import openmc
import os

from vr1.core import VR1core
from vr1.settings import SettingsOpenMC


class WriterOpenMC:
    """ OpenMC writer for the VR1 models """
    def __init__(self, settings: SettingsOpenMC, core: VR1core) -> None:
        self.output_dir: str = 'vr1'
        self.core = core
        self.settings = settings
        openmc.config['cross_sections'] = self.settings.xs_xml
        self.openmc_materials = openmc.Materials()
        self.openmc_geometry = openmc.Geometry()
        self.openmc_settings = openmc.Settings()
        self.openmc_tallies = openmc.Tallies()
        self.openmc_model = openmc.Model()

    def set_settings(self) -> openmc.Settings:
        """ Creates OpenMC settings object """
        settings = openmc.Settings()
        settings.batches = self.settings.parm['gen']
        settings.particles = self.settings.parm['npg']
        settings.generations_per_batch = self.settings.generations_per_batch
        settings.inactive = self.settings.parm['nsk']
        if self.settings.parm['sig']:
            settings.keff_trigger = {
            'type': 'std_dev',
            'threshold': self.settings.parm['sig']  # Ensure k-effective converges to this precision
        }
        settings.temperature = {'method': 'interpolation'}
        settings.source = openmc.IndependentSource(
            space=openmc.stats.Box(self.core.source_lower_left, self.core.source_upper_right),
            constraints={'fissionable': True}
        )
        return settings

    def set_tallies(self) -> openmc.tallies:
        """ Creates OpenMC tallies object """
        my_tallies: list = []
        for t in self.settings.tallies:
            my_tallies.append(t.get())
        return openmc.Tallies(my_tallies)

    def write_openmc_XML(self) -> int:
        """ Generates self.openmc_model and writes OpenMC XML deck corresponding to the underlying model & settings """
        if not os.path.isdir(self.output_dir):
            raise ValueError(f'Output directory {self.output_dir} does not exist')
        if not os.access(self.output_dir, os.W_OK):
            raise ValueError(f'Output directory {self.output_dir} does not have write access')
        #
        # if '3d' in self.settings.geom_mode.lower():
        #     raise ValueError('Not implemented yet')
        # elif '2.5d' in self.settings.geom_mode.lower():
        #     raise ValueError('Not implemented yet')
        # elif 'pincell' in self.settings.geom_mode.lower():
        #     for material in self._comp():
        #         if material.name in ['graphite', 'fuel']:
        #             self.openmc_materials.append(material)
        #     self.openmc_geometry = self._pincell()
        #
        # elif 'lattice' in self.settings.geom_mode.lower():
        #     raise ValueError('Not implemented yet')
        # else:
        #     raise ValueError(f'Geometry mode {self.settings.geom_mode} not implemented')

        self.openmc_settings = self.set_settings()
        self.openmc_tallies = self.set_tallies()

        """ Build the model object """
        self.openmc_model.materials = self.openmc_materials
        self.openmc_model.geometry = self.openmc_geometry
        self.openmc_model.settings = self.openmc_settings
        self.openmc_model.tallies = self.openmc_tallies

        self.openmc_model.export_to_model_xml(self.output_dir, remove_surfs=True)
        return 0
