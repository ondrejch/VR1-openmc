"""Tests for GUI-adjacent logic that is safe to run headless."""

from __future__ import annotations

import pytest

from vr1.gui import DEFAULT_COMPONENT_TYPES, parse_lattice_configuration
from vr1.utils import launch_lattice_builder


def test_parse_lattice_configuration_assignment() -> None:
    """Parser should read a ``*_LATTICE`` assignment safely."""
    content = """CUSTOM_LATTICE = [
['w','w','w','w','w','w','w','w'],
['w','8','8','8','8','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
]"""
    lattice = parse_lattice_configuration(content, allowed_components=DEFAULT_COMPONENT_TYPES)
    assert lattice[1][1] == "8"
    assert len(lattice) == 8
    assert all(len(row) == 8 for row in lattice)


def test_parse_lattice_configuration_rejects_unknown_component() -> None:
    """Parser should reject invalid cell identifiers."""
    content = """CUSTOM_LATTICE = [
['w','w','w','w','w','w','w','w'],
['w','BAD','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
['w','w','w','w','w','w','w','w'],
]"""
    with pytest.raises(ValueError):
        parse_lattice_configuration(content, allowed_components=DEFAULT_COMPONENT_TYPES)


def test_utils_integration() -> None:
    """Lattice-launch function should remain importable and callable."""
    assert callable(launch_lattice_builder), "launch_lattice_builder is not callable"
