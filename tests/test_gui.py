"""Tests for the VR1 Lattice Builder GUI helpers (no display needed)."""

from __future__ import annotations

import pytest

pytest.importorskip("tkinter")

from vr1.gui import DEFAULT_COMPONENT_TYPES, is_valid_component, parse_lattice_configuration


def _export(lattice: list[list[str]]) -> str:
    """Same text as VR1LatticeBuilder.export_configuration writes."""
    return "CUSTOM_LATTICE = [\n" + "".join(f"    {row},\n" for row in lattice) + "]\n\n"


def test_exported_configuration_can_be_loaded_back() -> None:
    """Codes the GUI accepts when typed must also load from an exported file."""
    lattice = [["w"] * 8 for _ in range(8)]
    lattice[2][2:6] = ["6_42.5", "4_10", "v12_6", "X4"]
    loaded = parse_lattice_configuration(_export(lattice))
    assert loaded == lattice
    assert all(is_valid_component(cell) for row in loaded for cell in row)


def test_preset_layouts_are_valid_components() -> None:
    """The shipped core designs only use codes the GUI accepts."""
    pytest.importorskip("openmc")
    from vr1.core import core_designs

    for lattice in core_designs.values():
        assert all(is_valid_component(cell) for row in lattice for cell in row)


def test_unknown_components_are_rejected() -> None:
    for code in ("v90", "6_", "v56_6", "0", "abc"):
        assert not is_valid_component(code)
    lattice = [["w"] * 8 for _ in range(8)]
    lattice[3][3] = "v90"
    with pytest.raises(ValueError, match='Unknown lattice component "v90"'):
        parse_lattice_configuration(_export(lattice), is_allowed=is_valid_component)


def test_gui_components_can_be_built() -> None:
    """Every code offered by the GUI is known to the lattice builder."""
    pytest.importorskip("openmc")
    from vr1.lattice_units import LatticeUnitVR1
    from vr1.materials import VR1Materials

    builder = LatticeUnitVR1(VR1Materials())
    builder.load()
    for code in DEFAULT_COMPONENT_TYPES + ["6_42.5", "4_10", "v12_6", "v25_d"]:
        builder.get(code)


def test_utils_integration() -> None:
    """launch_lattice_builder is exposed by vr1.utils."""
    pytest.importorskip("openmc")
    from vr1.utils import launch_lattice_builder

    assert callable(launch_lattice_builder)
