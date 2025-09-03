""" OpenMC model writer for VR1 """

import openmc
import os
from vr1.core import VR1core
from vr1.materials import vr1_materials
from vr1.settings import SettingsOpenMC


class WriterOpenMC:
    """ OpenMC writer for the VR1 models """
    def __init__(self, settings: SettingsOpenMC, core: VR1core) -> None:
        """Initializes a class with settings and core parameters to set up the OpenMC model.
        Parameters:
            - settings (SettingsOpenMC): Configuration settings for the OpenMC simulation.
            - core (VR1core): The core specification for the VR1 reactor model.
        Returns:
            - None: This constructor does not return a value."""
        self.output_dir: str = 'vr1'
        self.core: VR1core = core
        self.settings = settings
        self.openmc_materials = vr1_materials.get_materials()
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
        if 'sig' in self.settings.parm:
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
        if self.settings.tallies:
            for t in self.settings.tallies:
                my_tallies.append(t)
        return openmc.Tallies(my_tallies)

    def set_plots(self) -> openmc.Plots:
        my_plots: list = []
        if self.settings.plots:
            for p in self.settings.plots:
                my_plots.append(p)
        return openmc.Plots(my_plots)

    def set_geometry(self) -> openmc.geometry:
        """ Creates OpenMC geometry object """
        if self.core:
            return openmc.Geometry(root=self.core.model)
        else:
            raise ValueError(f'Cannot create geometry for {self.core}')

    def write_openmc_XML(self) -> int:
        """ Generates self.openmc_model and writes OpenMC XML deck corresponding to the underlying model & settings """
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
            # raise ValueError(f'Output directory {self.output_dir} does not exist')
        if not os.access(self.output_dir, os.W_OK):
            raise ValueError(f'Output directory {self.output_dir} does not have write access')

        self.openmc_settings = self.set_settings()
        self.openmc_tallies = self.set_tallies()
        self.openmc_geometry = self.set_geometry()
        self.openmc_geometry.merge_surfaces = True
        self.openmc_materials.cross_section_library = self.settings.xs_lib
        self.openmc_materials.cross_sections = self.settings.xs_xml

        """ Build the model object """
        self.openmc_model.materials = self.openmc_materials
        self.openmc_model.geometry = self.openmc_geometry
        self.openmc_model.settings = self.openmc_settings
        self.openmc_model.tallies = self.openmc_tallies
        self.openmc_model.plots = self.set_plots()
        self.openmc_model.export_to_model_xml(self.output_dir)
        return 0
