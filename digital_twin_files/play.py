import os
import sys
from pathlib import Path

# Ensure parent package imports work even when running this file directly.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Keep all generated files in this script's directory.
os.chdir(HERE)

import vr1
from vr1.core import FuelAssembly, Lattice
from vr1.settings import VR1Settings
from vr1.writer import WriterOpenMC
from vr1.plots import test_plots
from vr1.materials import VR1Materials
from vr1.VR1facility import Facility
import vr1.lattice_units as vlu
import openmc
import openmc.deplete
import openmc.stats
from vr1.core import core_designs
from vr1.utils import replace_water_fill

openmc.Materials.cross_sections = "/home/sg44769/openmc-data/endfb-viii.0-hdf5/cross_sections.xml"
# chainfile = "/home/sg44769/openmc-data/chainfile.xml"
mats = VR1Materials()

# create bubbly water at specified density
dummy_water_density_multiplier = 1.00
fuel_assembly_water_density_multiplier = 1.00
dummy_water_material = mats.create_water_with_bubbles(dummy_water_density_multiplier, name='water_bubbles_dummy')
fuel_assembly_water_material = mats.create_water_with_bubbles(fuel_assembly_water_density_multiplier, name='water_bubbles_fa')

materials = mats.get_materials() #generates materials obj
materials.export_to_xml()


# absorption_rod = vlu.AbsRod(materials=mats)
assembly = vlu.IRT4M(materials=mats,fa_type='8')
facility = Facility(materials=mats)
gridplate = vlu.GridPlate(materials=mats)

# self.lattice_unit_builders: dict = {
#     '8': IRT4M(fa_type='8',materials=self.materials),
#     '6': IRT4M(fa_type='6',materials=self.materials),
#     '4': IRT4M(fa_type='4',materials=self.materials),
#     'v90': VertChannel(materials=self.materials,diameter=90),
#     'v56': VertChannel(materials=self.materials,diameter=56),
#     'v30': VertChannel(materials=self.materials,diameter=30),
#     'v25': VertChannel(materials=self.materials,diameter=25),
#     'v12': VertChannel(materials=self.materials,diameter=12),
#     'O': AbsRod(materials=self.materials, assembly_type='6',rod_height=84.7), #fully removed control rod
#     'X': AbsRod(materials=self.materials, assembly_type='6',rod_height=0), #fully inserted control rod
#     'G': Reflector(materials=self.materials,reflector_type=self.materials.graphite),
#     'B': Reflector(materials=self.materials,reflector_type=self.materials.beryllium),
#     'd': Dummy(materials=self.materials),
#     'rt': Dummy(materials=self.materials,RT=True),
#     'w':   Water(materials=self.materials),
#     'wrc': Water(materials=self.materials,RC=True),
# }



# Control rod height can range from 0 cm (fully inserted) to 84.7 cm (fully removed) in the IRT-4M assembly.
cr1_height = 84.7
cr2_height = 84.7

lattice_default = [['w','w','w','w','w','w','w','w'],
                    ['w','w','v56','w','v25','w','w','w'],
                    ['w','w','6','8',f'6_{cr1_height}','8','w','w'],
                    ['w','w','d','O','8','X','w','w'],
                    ['v56','w','v12_6','8','O','8','v30','w'],
                    ['w','w','v12_d','O','d','8','w','w'],
                    ['w','w','6','8',f'6_{cr2_height}','8','w','w'],
                    ['w','w','w','w','w','w','w','w']]


dummy = vlu.Dummy(materials=mats,RT=True)
rabbit = vlu.RabbitTube(materials=mats)
lattice = Lattice(materials=mats,lattice_str=lattice_default)


# --- Replace one Dummy assembly at (row, col) e.g. (3,4) ---
dummy_uni = vlu.Dummy(materials=mats).build()
replace_water_fill(dummy_uni, mats, dummy_water_material)
lattice.lattice.universes[3][4] = dummy_uni   # put the modified universe into the lattice

# --- Replace one Fuel Assembly at (row, col) e.g. (5,4) ---
assembly_uni = vlu.IRT4M(materials=mats, fa_type='8').build()
replace_water_fill(assembly_uni, mats, fuel_assembly_water_material)
lattice.lattice.universes[5][4] = assembly_uni


uni_facility_lattice = facility.build(lattice)
uni_dummy = dummy.build()
uni_rabbit = rabbit.build()
uni_grid = gridplate.build()

geometry = openmc.Geometry(root=uni_facility_lattice)
geometry.export_to_xml()

### Tally Setup
tallies = openmc.Tallies()
mesh = openmc.RegularMesh()
mesh.lower_left = (-30.0, -30.0, 0.0)
mesh.upper_right = (30.0, 30.0, 70.0)
mesh.dimension = (60, 60, 70) 
mesh_filter = openmc.MeshFilter(mesh)

energy_bins = [0.0, 0.625, 20.0e6]
energy_filter = openmc.EnergyFilter(energy_bins)

mesh_tally = openmc.Tally(name='3D_Cartesian_Mesh_Tally')
mesh_tally.filters = [mesh_filter, energy_filter]
mesh_tally.scores = ['flux']

tallies = openmc.Tallies([mesh_tally])
tallies.export_to_xml()


settings = openmc.Settings()
settings.run_mode = 'eigenvalue'
settings.temperature = {'method':'interpolation'}
settings.batches = 1000
settings.inactive = 800
settings.particles = 10000
settings.photon_transport = False
source_area = openmc.stats.Box(lattice.source_lower_left,lattice.source_upper_right)

settings.source_rejection_fraction = 0.01

# settings.source = openmc.FileSource('statepoint.1000.h5')
settings.source = openmc.IndependentSource(space=source_area, constraints={'fissionable': True})
settings.export_to_xml()

# Uncomment below to visualize with openmc-plotter (requires GUI environment)
import vr1.utils
# vr1.utils.plot_vr1()

openmc.run()
