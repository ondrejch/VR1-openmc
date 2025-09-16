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
- Validate OpenMC results against Serpent models and experimental data
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

## Installation Guide - Conda
These steps show you how to install the VR1-openmc package using conda. 

1. Make sure you have conda installed.
2. **Install openmc using conda-forge or mamba.** OpenMC is a dependency for VR1. Instructions can be found on [OpenMC's website](https://docs.openmc.org/en/stable/quickinstall.html).
3. Create a new conda environment with Python 3.11 and activate it:
```
conda create -n vr1 python=3.11 openmc -c conda-forge
conda activate vr1
```
3. Install the VR1 package from GitHub
```
pip install git+https://github.com/ondrejch/VR1-openmc.git
```
4. You can now use the VR1 digital twin tools in your Python scripts or Jupyter notebooks. Try doing `import vr1` and it should work.
5. You can also clone the repo using
```
git clone https://github.com/ondrejch/VR1-openmc.git
cd VR1-openmc
pip install -e .
```

## Installation Guide - venv

1. Make and activate a virtual environment.
```
python -m venv vr1-venv
source vr1-venv/bin/activate
```
2. Install OpenMC into the virtual environment. This assumes you have cloned and build OpenMC already.  
```
pip install <path to>/openmc/
```
3. Install vr-1 package from GitHub
```
git clone git@github.com:ondrejch/VR1-openmc.git
cd VR1-openmc
pip install -r requirements.txt
pip install .
```
Likely there is a more elegant way, but this works. 

## Visualization Using OpenMC-Plotter

1. The best way to visualize OpenMC geometry is using OpenMC's development branch feature: OpenMC-Plotter. \n
To install with PyPI:

``` 
python -m pip install openmc-plotter
```

To install with conda (recommended if you're using a conda environment):

```
conda install -c conda-forge openmc-plotter
```

2. To use openmc-plotter, you must have an OpenMC model generated (at least "settings.xml," "geomtetry.xml," and "materials.xml"). Then, run

```
openmc-plotter <path_to_openmc_model_dir>
```

or if you're already in the directory with the necessarily xml files you can run

```
openmc-plotter
```

3. If you encounter the error

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

