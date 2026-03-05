# VR1 OpenMC Model

OpenMC model of the VR-1 research reactor (CTU Prague), including:
- core/facility geometry builders (`vr1/`)
- material and tally definitions
- plotting helpers
- point-kinetics solver (`pke/`)

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

## Repository Structure

- `vr1/`: main VR-1 geometry/material/tally/settings/writer code
- `pke/`: point kinetics solver and examples
- `tests/`: unit/integration tests
- `scratch/`: exploratory scripts
