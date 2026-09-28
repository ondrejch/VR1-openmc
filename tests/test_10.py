"""Integration tests for VR-1 model construction and XML export."""

from __future__ import annotations

from pathlib import Path

import pytest

openmc = pytest.importorskip("openmc")

from vr1.core import Lattice
from vr1.materials import VR1Materials
from vr1.settings import VR1Settings
from vr1.writer import WriterOpenMC


def test_writer_generates_model_xml(tmp_path: Path) -> None:
    """Writer should generate a model XML deck with normalized settings keys."""
    materials = VR1Materials()
    core = Lattice(materials=materials, lattice_str=[['w'] * 8 for _ in range(8)])
    settings = VR1Settings(
        xs_xml="/tmp/nonexistent-cross-sections.xml",
        parm={"npg": 50, "batches": 8, "inactive": 2},
    )
    writer = WriterOpenMC(settings=settings, core=core)
    writer.output_dir = str(tmp_path)
    assert writer.write_openmc_XML() == 0
    assert (tmp_path / "model.xml").is_file()


def test_lattice_accepts_named_preset() -> None:
    """Lattice should accept preset names via core_designs."""
    materials = VR1Materials()
    lattice = Lattice(materials=materials, preset="C12-C-2023")
    assert lattice.model is not None


def test_lattice_rejects_invalid_preset_type() -> None:
    """Preset must be either a name or a lattice list."""
    materials = VR1Materials()
    with pytest.raises(TypeError):
        Lattice(materials=materials, preset=True)


def test_writer_sets_fissionable_box_source(tmp_path: Path) -> None:
    """Without external sources, the writer uses the core's fissionable box source."""
    materials = VR1Materials()
    core = Lattice(materials=materials, preset="C12-C-2023")
    writer = WriterOpenMC(settings=VR1Settings(parm={"npg": 50, "batches": 8, "inactive": 2}), core=core)
    settings = writer.set_settings()
    assert len(settings.source) == 1
    space = settings.source[0].space
    assert tuple(space.lower_left) == tuple(core.source_lower_left)
    assert tuple(space.upper_right) == tuple(core.source_upper_right)


def test_scram_only_changes_control_rod_positions() -> None:
    """SCRAM/unSCRAM must keep the rod's FA type and leave channels in assemblies alone."""
    materials = VR1Materials()
    lattice_str = [["w"] * 8 for _ in range(8)]
    lattice_str[1][1:7] = ["v12_6", "v12_d", "6_30", "4_30", "O4", "O"]
    core = Lattice(materials=materials, lattice_str=lattice_str)
    core.SCRAM()
    assert core.lattice_str[1][1:7] == ["v12_6", "v12_d", "X", "X4", "X4", "X"]
    core.unSCRAM()
    assert core.lattice_str[1][1:7] == ["v12_6", "v12_d", "O", "O4", "O4", "O"]


def test_radial_channel_override_warns_about_replaced_units() -> None:
    """Units placed under the radial channel are replaced by 'wrc' with a warning."""
    materials = VR1Materials()
    lattice_str = [["w"] * 8 for _ in range(8)]
    lattice_str[7][3] = "v56"
    with pytest.warns(UserWarning, match=r"\[7\]\[3\]='v56'"):
        core = Lattice(materials=materials, lattice_str=lattice_str)
    assert core.lattice_str[7][2:6] == ["wrc"] * 4
