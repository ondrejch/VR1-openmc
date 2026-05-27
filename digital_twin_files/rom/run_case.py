import argparse
import csv
import os
import sys
from pathlib import Path
import numpy as np
import openmc

# Ensure parent package imports work
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def setup_run_directory(case_id: int):
    run_dir = HERE / f"run_{case_id}"
    run_dir.mkdir(exist_ok=True)
    os.chdir(run_dir)

    # NEW: Scrub old HDF5 files to prevent TACC Lustre lock collisions
    for h5_file in Path('.').glob('*.h5'):
        try:
            h5_file.unlink()
        except OSError:
            pass # Ignore if it can't be deleted, though it usually succeeds

    return run_dir


# Import VR1 modules AFTER setting paths
from vr1.materials import VR1Materials
from vr1.VR1facility import Facility
import vr1.lattice_units as vlu
from vr1.core import Lattice
from vr1.utils import replace_water_fill


def read_configuration(csv_path: Path, target_case_id: int) -> dict:
    """Reads the specific row from the LHS CSV based on case_id."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['case_id']) == target_case_id:
                return {
                    'cr1_height': float(row['cr1_height']),
                    'cr2_height': float(row['cr2_height']),
                    'dummy_water_density': float(row['dummy_water_density_multiplier']),
                    'fa_water_density': float(row['fuel_assembly_water_density_multiplier'])
                }
    raise ValueError(f"case_id {target_case_id} not found in {csv_path}")

def build_and_run_openmc(config: dict, case_id: int):
    """Your play.py logic wrapped in a function."""

    openmc.Materials.cross_sections = "/corral-secure/utexas/ASC23046/OpenMC_XS_Libraries/endfb-viii.0-hdf5/cross_sections.xml"
    mats = VR1Materials()

    # Apply LHS Densities
    dummy_water_material = mats.create_water_with_bubbles(config['dummy_water_density'], name='water_bubbles_dummy')
    fuel_assembly_water_material = mats.create_water_with_bubbles(config['fa_water_density'], name='water_bubbles_fa')

    materials = mats.get_materials()
    materials.export_to_xml()

    assembly = vlu.IRT4M(materials=mats, fa_type='8')
    facility = Facility(materials=mats)
    gridplate = vlu.GridPlate(materials=mats)

    # Apply LHS Rod Heights
    cr1_height = config['cr1_height']
    cr2_height = config['cr2_height']

    lattice_default = [
        ['w','w','w','w','w','w','w','w'],
        ['w','w','v56','w','v25','w','w','w'],
        ['w','w','6','8',f'6_{cr1_height}','8','w','w'],
        ['w','w','d','O','8','X','w','w'],
        ['v56','w','v12_6','8','O','8','v30','w'],
        ['w','w','v12_d','O','d','8','w','w'],
        ['w','w','6','8',f'6_{cr2_height}','8','w','w'],
        ['w','w','w','w','w','w','w','w']
    ]

    dummy = vlu.Dummy(materials=mats, RT=True)
    rabbit = vlu.RabbitTube(materials=mats)
    lattice = Lattice(materials=mats, lattice_str=lattice_default)

    # Apply Density Multipliers to specific assemblies
    dummy_uni = vlu.Dummy(materials=mats).build()
    replace_water_fill(dummy_uni, mats, dummy_water_material)
    lattice.lattice.universes[5][4] = dummy_uni

    assembly_uni = vlu.IRT4M(materials=mats, fa_type='8').build()
    replace_water_fill(assembly_uni, mats, fuel_assembly_water_material)
    lattice.lattice.universes[3][4] = assembly_uni

    uni_facility_lattice = facility.build(lattice)
    geometry = openmc.Geometry(root=uni_facility_lattice)
    geometry.export_to_xml()

    ### Tally Setup
    mesh = openmc.RegularMesh()
    mesh.lower_left = (-30.0, -30.0, 0.0)
    mesh.upper_right = (30.0, 30.0, 70.0)
    mesh.dimension = (120, 120, 70)
    mesh_filter = openmc.MeshFilter(mesh)

    energy_bins = [0.0, 1, 100e3, 20.0e6]
    energy_filter = openmc.EnergyFilter(energy_bins)

    mesh_tally = openmc.Tally(name='3D_Cartesian_Mesh_Tally')
    mesh_tally.filters = [mesh_filter, energy_filter]
    mesh_tally.scores = ['flux']

    tallies = openmc.Tallies([mesh_tally])
    tallies.export_to_xml()

    settings = openmc.Settings()
    settings.run_mode = 'eigenvalue'
    settings.temperature = {'method':'interpolation'}
    settings.batches = 500
    settings.inactive = 20
    settings.particles = 100000
    settings.photon_transport = False

    # You might want to remove the specific statepoint source for pure LHS parameter sweeps
    # to avoid dimensional mismatches if geometry changes drastically,
    # but I left it here based on your script.
    settings.source = openmc.FileSource('../statepoint.1000.h5')
    settings.export_to_xml()

    # Run OpenMC using TACC's MPI launcher
    # openmc.run(mpi_args=['ibrun'])
    # Grab the OMP_NUM_THREADS from the SLURM environment, default to 32
    threads = int(os.environ.get('OMP_NUM_THREADS', 32))
    openmc.run(threads=threads, event_based=False)


def extract_and_save_data(case_id: int):
    """Extracts k_eff and the flattened flux vectors for the POD matrix."""
    sp = openmc.StatePoint('statepoint.500.h5')

    keff = sp.k_combined.nominal_value
    keff_std = sp.k_combined.std_dev

    tally = sp.get_tally(name='3D_Cartesian_Mesh_Tally')

    # get_values returns an array of shape (N_mesh_cells * N_energy_groups, 1, 1)
    # We want to separate the thermal, intermediate, and fast flux and flatten them for the POD snapshot matrix
    flux_data = tally.get_values(scores=['flux']).flatten()

    # Because of how OpenMC structures the tally array with a 3-group energy filter:
    # Every 3rd (0, 3, 6...) = group 1 (thermal: 0.0 to 1 eV)
    # Every 3rd (1, 4, 7...) = group 2 (intermediate: 1 to 100 keV)
    # Every 3rd (2, 5, 8...) = group 3 (fast: 100 keV to 20 MeV)
    thermal_flux_vector = flux_data[0::3]
    intermediate_flux_vector = flux_data[1::3]
    fast_flux_vector = flux_data[2::3]

    # Save to a compressed numpy file for easy loading in your Jupyter Notebook later
    np.savez_compressed(
        f"../results_case_{case_id}.npz",
        case_id=case_id,
        keff=keff,
        keff_std=keff_std,
        thermal_flux=thermal_flux_vector,
        intermediate_flux=intermediate_flux_vector,
        fast_flux=fast_flux_vector
    )
    print(f"Case {case_id} complete. Results saved.")


def main():
    parser = argparse.ArgumentParser(description="Run a single VR1 configuration for TACC array job.")
    parser.add_argument("--case_id", type=int, required=True, help="The case_id from the LHS CSV.")
    parser.add_argument("--csv", type=Path, default=HERE / "training_set.csv", help="Path to LHS CSV.")
    args = parser.parse_args()

    config = read_configuration(args.csv, args.case_id)

    # Isolate runs in their own directories so OpenMC XMLs don't overwrite each other in parallel
    setup_run_directory(args.case_id)

    print(f"Running Case {args.case_id} with config: {config}")
    build_and_run_openmc(config, args.case_id)
    extract_and_save_data(args.case_id)

if __name__ == "__main__":
    main()