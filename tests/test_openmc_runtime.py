"""OpenMC-dependent runtime regression tests."""

from __future__ import annotations

from pathlib import Path

import pytest

openmc = pytest.importorskip("openmc")

from vr1.lattice_units import IRT4M, surfaces
from vr1.materials import VR1Materials, vr1_materials
from vr1.settings import VR1Settings
from vr1.tallies import FluxTally


def test_flux_tally_exports_with_scores_and_energy_bins(tmp_path: Path) -> None:
    """Flux tally should define scores and use valid energy-bin ordering."""
    tally = FluxTally(vr1_materials, "fuel flux").get()
    tallies = openmc.Tallies([tally])
    output = tmp_path / "tallies.xml"
    tallies.export_to_xml(path=output)
    assert output.is_file()
    assert tally.scores == ["flux"]


def test_reflective_boundary_state_does_not_leak_between_builds() -> None:
    """A reflective assembly build must not force later builds to reflective."""
    IRT4M(materials=vr1_materials, fa_type="6", boundary="reflective").build()
    assert surfaces["FAZ.2"].boundary_type == "reflective"
    IRT4M(materials=vr1_materials, fa_type="6", boundary="water").build()
    assert surfaces["FAZ.2"].boundary_type == "transmission"


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
