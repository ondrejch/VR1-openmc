"""OpenMC-dependent runtime regression tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

openmc = pytest.importorskip("openmc")

from vr1.core import FuelAssembly, Lattice
from vr1.lattice_units import IRT4M, AbsRod, surfaces
from vr1.materials import VR1Materials, vr1_materials
from vr1.settings import VR1Settings
from vr1.tallies import FluxTally
from vr1.utils import replace_water_fill


def test_flux_tally_exports_with_scores_and_energy_bins(tmp_path: Path) -> None:
    """Flux tally should define scores and use valid energy-bin ordering."""
    tally = FluxTally(vr1_materials, "fuel flux").get()
    tallies = openmc.Tallies([tally])
    output = tmp_path / "tallies.xml"
    tallies.export_to_xml(path=output)
    assert output.is_file()
    assert tally.scores == ["flux"]


def _boundary_types(universe: openmc.Universe) -> set[str]:
    return {s.boundary_type for s in openmc.Geometry(universe).get_all_surfaces().values()}


def test_reflective_boundary_state_does_not_leak_between_builds() -> None:
    """Reflective builds keep their own boundaries and leave shared surfaces alone."""
    reflective = IRT4M(materials=vr1_materials, fa_type="6", boundary="reflective").build()
    assert surfaces["FAZ.2"].boundary_type == "transmission"
    water = IRT4M(materials=vr1_materials, fa_type="6", boundary="water").build()
    IRT4M(materials=vr1_materials, fa_type="8").build()
    assert "reflective" in _boundary_types(reflective)
    assert "reflective" not in _boundary_types(water)


def test_reflective_abs_rod_keeps_reflective_boundary() -> None:
    """The nested fuel-assembly build must not undo the rod's reflective boundary."""
    rod = AbsRod(materials=vr1_materials, assembly_type="6", boundary="reflective").build()
    assert "reflective" in _boundary_types(rod)


@pytest.mark.parametrize(("fa_type", "n_tubes"), [("X", 6), ("O", 6), ("X4", 4), ("O4", 4)])
def test_rodded_fuel_assembly_contains_absorber(fa_type: str, n_tubes: int) -> None:
    """Rodded FuelAssembly codes build the FA with its absorber rod, not a plain FA."""
    model = FuelAssembly(fa_type).model
    materials = {m.name for m in model.get_all_materials().values()}
    assert "cdlayer" in materials
    cells = {c.name for c in model.get_all_cells().values()}
    assert f"mid_f_{n_tubes}" in cells and f"mid_f_{n_tubes + 1}" not in cells


def test_plain_fuel_assembly_has_no_absorber() -> None:
    materials = {m.name for m in FuelAssembly("6").model.get_all_materials().values()}
    assert "cdlayer" not in materials


def test_replace_water_fill_recurses_into_lattices() -> None:
    """Water inside lattice universes is replaced too."""
    mats = VR1Materials()
    new_water = mats.create_water_with_bubbles(0.9)
    core = Lattice(materials=mats, lattice_str=[["w"] * 8 for _ in range(8)])
    assert replace_water_fill(core.model, mats, new_water) > 0
    fills = {c.fill.name for c in core.model.get_all_cells().values() if isinstance(c.fill, openmc.Material)}
    assert mats.water.name not in fills


def test_material_mappings_use_expected_compositions() -> None:
    """Lead and steel materials should map to their intended nuclide sets."""
    mats = VR1Materials()
    lead_nuclides = {n.name for n in mats.lead.nuclides}
    steel_nuclides = {n.name for n in mats.steelrc.nuclides}
    assert "Pb208" in lead_nuclides
    assert "Al27" not in lead_nuclides
    assert "Fe56" in steel_nuclides


def test_settings_reject_invalid_parameter_keys() -> None:
    """Settings validation should reject missing required run-parameter keys."""
    with pytest.raises(ValueError):
        VR1Settings(parm={"npg": 1000, "gen": 110, "nsk": 10})


def test_settings_accept_zero_inactive_and_numpy_integers() -> None:
    """OpenMC accepts zero inactive batches and numpy integers."""
    settings = VR1Settings(parm={"npg": np.int64(100), "batches": 20, "inactive": 0}).get_settings()
    assert settings.inactive == 0
    assert settings.particles == 100
    with pytest.raises(ValueError):
        VR1Settings(parm={"npg": 0, "batches": 20, "inactive": 0})
