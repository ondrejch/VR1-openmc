from vr1.core import FuelAssembly, TestLattice
from vr1.settings import SettingsOpenMC
from vr1.writer import WriterOpenMC

my_settings = SettingsOpenMC()
my_core = TestLattice()
my_writer = WriterOpenMC(my_settings, my_core)
my_writer.write_openmc_XML()
