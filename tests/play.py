from vr1.core import FuelAssembly, TestLattice
from vr1.settings import SettingsOpenMC
from vr1.writer import WriterOpenMC
from vr1.plots import test_plots
from vr1.materials import VR1Materials
import vr1.lattice_units as vlu
import vr1
import openmc

# my_settings = SettingsOpenMC()
# my_settings.plots = test_plots()
# my_core = TestLattice()
# my_writer = WriterOpenMC(my_settings, my_core)
# my_writer.write_openmc_XML()

openmc.Materials.cross_sections = "/Users/macris/openmc_data/endfb-viii.0-hdf5/cross_sections.xml" #must do this to get C12

mats = VR1Materials()
mats.get_materials() #generates materials.xml for plotting

absorption_rod = vlu.AbsRod(materials=mats)
assembly = vlu.IRT4M(materials=mats,fa_type='8')
facility = vlu.Facility(materials=mats)
latticetest: list[list[str]] = [
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
    ['6', '6', '6', '6', '6', '6', '6', '6'],
]

lattice = TestLattice(materials=mats,lattice_str=latticetest)

# uni_abs = absorption_rod.build(rod_height=100)
uni_assembly = vlu.assembly.build()

# uni_facility = vr1.VR1Facility.Facility.build()

uni_facility_lattice = vr1.VR1Facility.Facility.build(lattice)

geo = openmc.Geometry(root=uni_facility_lattice)
geo.export_to_xml()
mod = openmc.Model()
mod.geometry = geo
plot=openmc.Plot()
plot.colors = {mats.air: 'pink', mats.water:'red', mats.abshead: 'lime', mats.abscenter: 'blue', mats.cdlayer: 'black',
               mats.grid: 'grey', mats.bottomnozzle: 'yellow', mats.guidetube:'orange', mats.fuel: 'cyan', mats.abstube: 'green'}
plot.width = (40, 40)
plot.pixels = (1000, 1000)
plot.origin = (0, 0, 0)
plot.basis = 'xz'
# mod.plots = openmc.Plots([plot])
plot.to_xml_element()