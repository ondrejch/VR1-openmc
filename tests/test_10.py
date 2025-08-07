from vr1.core import FuelAssembly, TestLattice
from vr1.settings import SettingsOpenMC
from vr1.writer import WriterOpenMC
from vr1.plots import test_plots
from vr1.materials import VR1Materials
import vr1.lattice_units as vlu
import vr1
import openmc

my_settings = SettingsOpenMC()
my_settings.plots = test_plots()
my_core = TestLattice()
my_writer = WriterOpenMC(my_settings, my_core)
my_writer.write_openmc_XML()
