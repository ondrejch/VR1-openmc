# VR1 OpenMC Model
## Overview

This repository contains an **OpenMC model of the VR1 research reactor**. The VR1 is a pool-type, light-water moderated research reactor located at the Czech Technical University in Prague.  Designed between 1985–1989 and achieving first criticality on 3~December~1990, the unit operates at a rated thermal power of 1~kW (with authorized excursions to 5~kW for short periods). The purpose of this github repo is to replicate the VR-1 geometry, materials, and operating conditions in OpenMC and benchmarking our results with the Czech **Serpent** simulation results.

## Project Goals

- Build a VR1 reactor core model in OpenMC
- Validate OpenMC results against Serpent or experimental data
- Provide reusable code for reactor physics training and education

## Repository Structure

- `/vr1`: Main source code for geometry, materials, tallies, plotting, and settings
- `/tests`: Automated tests for code correctness
- `/pke`: (Purpose TBD; possibly kinetics or standalone tools)
- `/scratch`: Experimental or prototype scripts
- `requirements.txt`: Dependencies for running the code
- `setup.py`: For package installation

## We have (4) Serpent input files for OpenMC-to-Serpent comparison: 
1. C12-C-2023_1 - Full current VR-1 core (critical state)
2. 6 – 6-tube IRT-4M fuel assembly
3. 8 – 8-tube IRT-4M fuel assembly
4. 6_with_abs_rod – 6-tube assembly with an inserted absorber rod

## Usage

1. **Install dependencies:** ```pip install -r requirements.txt```
2. ... Add more information here. 
