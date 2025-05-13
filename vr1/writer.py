
import openmc
import os
from dataclasses import dataclass

from vr1.core import VR1core
from vr1.settings import OpenMCSettings


@dataclass
class RectangularPrismBoundaryTypes():
    xmin: str
    xmax: str
    ymin: str
    ymax: str
    zmin: str
    zmax: str


class WriterOpenMC:
    """ OpenMC writer for the VR1 models """
    def __init__(self, settings: OpenMCSettings, core: VR1core) -> None:
        self.output_dir: str = 'vr1'
        self.core = core
        self.settings = settings
        self.openmc_materials = openmc.Materials()
        self.openmc_geometry = openmc.Geometry()
        self.openmc_settings = openmc.Settings()
        self.openmc_tallies = openmc.Tallies()
        self.openmc_model = openmc.Model()

    def _xs_lib_paths(self) -> str:
        openmc.config['cross_sections'] = self.settings.xs_xml
        return "Cross-section library path set."

    def _header(self) -> str:
        """
        Outputs the header string for the OpenMC deck
        gives:  the run parameters
                the name of the file
                the cross-section library
        """
        header_output: str = f'set title "{self.model.name} {self.settings.my_time_now}"\n\n'
        return header_output

    def _comp(self) -> openmc.Materials:
        pass

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

        self.openmc_settings = self._settings()
        self.openmc_tallies = self._tallies()

        """ Build the model object """
        self.openmc_model.materials = self.openmc_materials
        self.openmc_model.geometry = self.openmc_geometry
        self.openmc_model.settings = self.openmc_settings
        self.openmc_model.tallies = self.openmc_tallies

        self.openmc_model.export_to_model_xml(self.output_dir)
        return 0
