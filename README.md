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

## Installation Guide 
These steps show you how to install the VR1-openmc package using conda. 

1. Make sure you have conda installed.
2. Create a new conda environment with Python 3.11 and activate it:
```
conda create -n vr1 python=3.11 openmc -c conda-forge
conda activate vr1
```
3. Install the VR1 package from github
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
