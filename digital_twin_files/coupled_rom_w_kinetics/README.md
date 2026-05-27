# Coupled ROM + Point Kinetics

This directory now keeps the small, self-contained coupled example in [simple_coupled_space_kinetics.py](simple_coupled_space_kinetics.py). The more complete coupled ROM and the visualization work are being moved into [quasi_static_coupled/](quasi_static_coupled/), which is future work.

## What This Script Does

[simple_coupled_space_kinetics.py](simple_coupled_space_kinetics.py) couples a standard point-kinetics solver with a nominal ROM flux shape. It is intentionally lightweight:

- it uses example-style reactivity transients: step, ramp, and sinusoidal
- it samples one nominal flux shape from the ROM
- it tracks local thermal and fast flux histories at three fixed points
- it saves a compact plot of the transient response

## How To Run It

From this directory, run:

```bash
python simple_coupled_space_kinetics.py
```

Optional arguments let you change the transient and output path:

```bash
python simple_coupled_space_kinetics.py \
  --transient ramp \
  --t-final 10.0 \
  --dt 0.001 \
  --out simple_coupled_space_kinetics.png
```

Supported transients are:

- `step`
- `ramp`
- `sinusoidal`

## Output

The script writes [simple_coupled_space_kinetics.png](simple_coupled_space_kinetics.png) by default. The plot shows normalized local thermal and fast flux histories at the three sample points, along with the imposed reactivity history.

## Future Work

The more detailed coupled workflow, including the old visualization helpers and generated summary artifacts, is being reorganized under [quasi_static_coupled/](quasi_static_coupled/). That subdirectory is the place for the next stage of the quasi-static and visualization-oriented work.