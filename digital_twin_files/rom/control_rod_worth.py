import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import openmc

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import vr1
from vr1.core import FuelAssembly, Lattice
from vr1.settings import VR1Settings
from vr1.writer import WriterOpenMC
from vr1.plots import test_plots
from vr1.materials import VR1Materials
from vr1.VR1facility import Facility
import vr1.lattice_units as vlu
from vr1.core import core_designs
import vr1.utils

os.chdir(HERE)

openmc.Materials.cross_sections = "/home/sg44769/openmc-data/endfb-viii.0-hdf5/cross_sections.xml"

vr1_materials = VR1Materials()
mats = vr1_materials.get_materials()
mats.export_to_xml()

keffs = []
keff_errs = []  # NEW: List to store standard deviations
rod_heights = [0,10,20,30,40,50,60,70,80,84.7]

R1_height = 0
E1_height = 0
R2_height = 0

batches = 40

for h in rod_heights:
    
    # TACC FIX: Scrub ALL old HDF5 files to prevent Lustre lock crashes during the loop
    for h5_file in Path('.').glob('*.h5'):
        try:
            h5_file.unlink()
        except OSError:
            pass

    vr1_materials = VR1Materials()
    mats = vr1_materials.get_materials()
    mats.export_to_xml()

    lattice_input =   [['w'  ,'w','w'    ,'w','w'  ,'w','w'  ,'w'],
                        ['w'  ,'w','v56'  ,'w','v25','w','w'  ,'w'],
                        ['w'  ,'w','6'    ,'8',f'6_{R1_height}'  ,'8','w'  ,'w'],
                        ['w'  ,'w','d'    ,'O','8'  ,f'6_{E1_height}','w'  ,'w'],
                        ['v56','w','v12_6','8','O'  ,'8','v30','w'],
                        ['w'  ,'w','v12_d','O','d'  ,'8','w'  ,'w'],
                        ['w'  ,'w','6'    ,'8',f'6_{h}','8'  ,'w'  ,'w'],
                        ['w'  ,'w','w'    ,'w','w','w'  ,'w'  ,'w']]

    lattice_obj = Lattice(materials=vr1_materials,lattice_str=lattice_input)

    facility_obj = Facility(materials=vr1_materials)
    vr1_model = facility_obj.build(lattice=lattice_obj)

    geometry = openmc.Geometry(root=vr1_model)
    geometry.export_to_xml()

    settings = openmc.Settings()
    settings.run_mode = 'eigenvalue'
    settings.temperature = {'method':'interpolation','range':(293.15,923.15)}
    settings.batches = batches
    settings.inactive = 15 
    settings.particles = 1000
    settings.photon_transport = True
    source_area = openmc.stats.Box(lattice_obj.source_lower_left,lattice_obj.source_upper_right)
    settings.source = openmc.Source(space=source_area,constraints={'fissionable': True})
    settings.export_to_xml()

    # TACC FIX: Grab OMP threads from environment
    threads = int(os.environ.get('OMP_NUM_THREADS', 32))
    openmc.run(threads=threads, event_based=False)

    with openmc.StatePoint(f'statepoint.{batches}.h5') as sp:
        k_eff = sp.keff.nominal_value
        k_err = sp.keff.std_dev  # NEW: Extract the uncertainty
        keffs.append(k_eff)
        keff_errs.append(k_err)  # NEW: Append to list

# NEW: Plotting with errorbars
# fmt='o-' adds points and a connecting line. capsize adds the little horizontal bars to the error lines.
plt.errorbar(rod_heights, keffs, yerr=keff_errs, fmt='o-', capsize=5, label='k-eff ± 1_sigma', color='blue')
plt.xlabel('Rod Height')
plt.ylabel('k-eff')
plt.suptitle('k-eff vs Control Rod Height')
plt.grid(True, linestyle='--', alpha=0.6) # Added a grid to make reading values easier
plt.legend()
plt.savefig(HERE / 'r1_fig.png')
