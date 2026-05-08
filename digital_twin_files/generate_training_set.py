from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class ParameterBounds:
    cr1_height: tuple[float, float] = (0.0, 84.7)
    cr2_height: tuple[float, float] = (0.0, 84.7)
    dummy_water_density_multiplier: tuple[float, float] = (0.50, 1.00)
    fuel_assembly_water_density_multiplier: tuple[float, float] = (0.50, 1.00)


PARAMETER_NAMES = (
    "cr1_height",
    "cr2_height",
    "dummy_water_density_multiplier",
    "fuel_assembly_water_density_multiplier",
)


def scale_samples(samples: np.ndarray, bounds: ParameterBounds) -> np.ndarray:
    lower = np.array(
        [
            bounds.cr1_height[0],
            bounds.cr2_height[0],
            bounds.dummy_water_density_multiplier[0],
            bounds.fuel_assembly_water_density_multiplier[0],
        ],
        dtype=float,
    )
    upper = np.array(
        [
            bounds.cr1_height[1],
            bounds.cr2_height[1],
            bounds.dummy_water_density_multiplier[1],
            bounds.fuel_assembly_water_density_multiplier[1],
        ],
        dtype=float,
    )
    return lower + samples * (upper - lower)


def generate_latin_hypercube(n_samples: int, seed: int | None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n_dimensions = 4
    samples = np.empty((n_samples, n_dimensions), dtype=float)

    for dimension in range(n_dimensions):
        cut_points = (np.arange(n_samples, dtype=float) + rng.random(n_samples)) / n_samples
        rng.shuffle(cut_points)
        samples[:, dimension] = cut_points

    return samples


def write_training_set(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(("case_id",) + PARAMETER_NAMES)
        for index, row in enumerate(data, start=1):
            writer.writerow([index, *row])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Latin hypercube training set for VR1 parametric runs."
    )
    parser.add_argument("-n", "--samples", type=int, default=100, help="Number of configurations to generate.")
    parser.add_argument("-s", "--seed", type=int, default=12345, help="Random seed for reproducibility.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("training_set.csv"),
        help="Output CSV path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bounds = ParameterBounds()
    unit_samples = generate_latin_hypercube(args.samples, args.seed)
    scaled_samples = scale_samples(unit_samples, bounds)
    write_training_set(args.output, scaled_samples)
    print(f"Wrote {args.samples} configurations to {args.output}")


if __name__ == "__main__":
    main()
