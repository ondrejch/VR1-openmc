# VR1 OpenMC Model
## Overview

This repository contains an **OpenMC model of the VR1 research reactor**. The VR1 is a pool-type, light-water moderated research reactor located at the Czech Technical University in Prague.  Designed between 1985–1989 and achieving first criticality on 3 December 1990, the unit operates at a rated thermal power of 1 kW (with authorized excursions to 5 kW for short periods). The purpose of this github repo is to replicate the VR-1 geometry, materials, and operating conditions in OpenMC and benchmarking our results with the Czech Serpent simulation results.

<div align="center">
  <img width="450" alt="Cross-section view of the VR1 reactor." src="https://github.com/user-attachments/assets/bf684307-44a0-48e8-93e5-52fa0b335b61" />
  <div style="margin-top: 8px; font-style: italic; color: #555;">
    <b>Figure 1:</b> Cross-section view of the VR-1 reactor.
  </div>
</div>

## Project Goals

- Build a VR1 reactor core model in OpenMC
- Validate OpenMC results against Serpent or experimental data
- Provide reusable code for reactor physics training and education

## Repository Structure

- `/vr1`: Main source code for geometry, materials, tallies, plotting, and settings
- `/tests`: Automated tests for code correctness
- `/pke`: Point kinetics solver
- `/scratch`: Experimental or prototype scripts
- `requirements.txt`: Dependencies for running the code
- `setup.py`: For package installation

## We have (4) Serpent input files for OpenMC-to-Serpent comparison: 
1. C12-C-2023_1 - Full current VR-1 core (critical state)
2. 6 – 6-tube IRT-4M fuel assembly
3. 8 – 8-tube IRT-4M fuel assembly
4. 6_with_abs_rod – 6-tube assembly with an inserted absorber rod

## Installation

### Option A: Conda (recommended)
```bash
conda env create -f environment.yml
conda activate vr1-openmc
```

### Option B: pip/venv
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Cross Section Data

OpenMC requires HDF5 nuclear data and a `cross_sections.xml` file.

Typical setup:
```bash
export OPENMC_CROSS_SECTIONS=/path/to/cross_sections.xml
```

You can also pass the path directly via `VR1Settings(xs_xml="...")`.

## Quick Usage

### Build an 8x8 lattice and export XML
```python
from vr1.core import Lattice
from vr1.materials import VR1Materials
from vr1.settings import VR1Settings
from vr1.writer import WriterOpenMC

materials = VR1Materials()
core = Lattice(materials=materials, preset="C12-C-2023")
settings = VR1Settings(
    xs_xml="/path/to/cross_sections.xml",
    parm={"npg": 5000, "batches": 110, "inactive": 10},
)

writer = WriterOpenMC(settings=settings, core=core)
writer.output_dir = "vr1_run"
writer.write_openmc_XML()
```

Expected output files in `vr1_run/`:
- `model.xml`

### Run GUI lattice builder
```python
from vr1.utils import launch_lattice_builder
launch_lattice_builder()
```

## Visualization Using OpenMC-Plotter

### OpenMC-Plotter Installation 
The best way to visualize OpenMC geometry is using OpenMC's development branch feature: OpenMC-Plotter. \n
To install with PyPI:

``` 
python -m pip install openmc-plotter
```

To install with conda (recommended if you're using a conda environment):

```
conda install -c conda-forge openmc-plotter
```

### OpenMC-Plotter Usage
To use openmc-plotter, you must have an OpenMC model generated (at least "settings.xml," "geomtetry.xml," and "materials.xml"). Then, run

```
openmc-plotter <path_to_openmc_model_dir>
```

or if you're already in the directory with the necessarily xml files you can run

```
openmc-plotter
```
### OpenMC-Plotter Issues

If you encounter the error

```
AttributeError: 'MainWindow' object has no attribute 'shortcutOverlay'
```

To fix this, run the following commands anywhere in Python. As of 07/09/2025, this was the only way to fix this on MacOS, but in theory it should work on any OS. 

```
from PySide6 import QtCore
settings = QtCore.QSettings()
settings.clear()
conda uninstall openmc-plotter
conda install -c conda-forge openmc-plotter
```

## Tests

Run tests:
```bash
pytest -q
```

OpenMC-dependent tests auto-skip when OpenMC is unavailable.

## HPC / SLURM Notes

Example SLURM script:
```bash
#!/bin/bash
#SBATCH --job-name=vr1-openmc
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=01:00:00
#SBATCH --partition=compute

module load openmc
source /path/to/venv/bin/activate
export OPENMC_CROSS_SECTIONS=/path/to/cross_sections.xml

python -c "from vr1.core import Lattice; from vr1.materials import VR1Materials; \
from vr1.settings import VR1Settings; from vr1.writer import WriterOpenMC; \
m=VR1Materials(); c=Lattice(materials=m,preset='C12-C-2023'); \
s=VR1Settings(xs_xml='$OPENMC_CROSS_SECTIONS'); \
w=WriterOpenMC(s,c); w.output_dir='run'; w.write_openmc_XML()"

cd run
srun openmc
```

## Reproducibility Notes

- Pin package versions (`requirements.txt` / `environment.yml`).
- Set OpenMC RNG seed in settings when needed for exact Monte Carlo reproducibility.
- Archive:
  - `model.xml`
  - OpenMC version
  - nuclear-data library version/path
