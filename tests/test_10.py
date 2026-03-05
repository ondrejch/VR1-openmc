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
