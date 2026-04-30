"""OpenMC settings container for VR-1 models."""

from __future__ import annotations

from datetime import datetime
import os
from typing import Any

import openmc

MY_TIME_NOW: str = datetime.now().isoformat(timespec="seconds")


class VR1Settings:
    """Store and validate simulation settings used by VR-1 model writers.

    Parameters
    ----------
    xs_xml : str | None, optional
        Path to OpenMC cross section XML file.
    xs_xml_root_path : str | None, optional
        Backward-compatible root path used to derive ``xs_xml`` as
        ``<root>/cross_sections.xml`` when ``xs_xml`` is not explicitly set.
    name : str, optional
        Label for the simulation.
    run_mode : str, optional
        OpenMC run mode, e.g. ``"eigenvalue"`` or ``"fixed source"``.
    tallies : list | None, optional
        Tally objects to include in the model.
    plots : list | None, optional
        Plot objects to include in the model.
    parm : dict[str, int] | None, optional
        Run controls with keys ``"npg"``, ``"batches"``, and ``"inactive"``.
    rotation : float, optional
        Reserved configuration value for model rotation.
    ext_sources : Any, optional
        External source object(s) accepted by ``openmc.Settings.source``.
    power : float | None, optional
        Total thermal power [W] used by depletion workflows.
    photon_transport : bool, optional
        Enable photon transport in OpenMC.
    """

    def __init__(
        self,
        xs_xml: str | None = None,
        xs_xml_root_path: str | None = None,
        name: str = "openmc deck",
        run_mode: str = "eigenvalue",
        tallies: list | None = None,
        plots: list | None = None,
        parm: dict[str, int] | None = None,
        rotation: float = 0.0,
        ext_sources: Any = None,
        power: float | None = None,
        photon_transport: bool = False,
    ) -> None:
        self.supported_code: str = "OpenMC"
        self.name = name
        self.my_time_now = MY_TIME_NOW
        self.hostname = os.uname()[1]

        # Backward-compatible root path handling.
        self.xs_xml_root_path = xs_xml_root_path
        if xs_xml is None and xs_xml_root_path:
            xs_xml = os.path.join(xs_xml_root_path, "cross_sections.xml")
        self.xs_xml = xs_xml
        self.xs_lib = None

        self.power = power  # [W_th]
        self.tallies = tallies
        self.plots = plots
        self.ext_sources = ext_sources
        self.rotation = rotation
        self.generations_per_batch: int = 1
        self.photon_transport = photon_transport
        self.run_mode = run_mode

        if parm is None:
            self.parm = {"npg": 1000, "batches": 110, "inactive": 10}
        else:
            self.parm = parm
        self.validate()

    def validate(self) -> None:
        """Validate run-parameter structure and values."""
        required = {"npg", "batches", "inactive"}
        missing = required.difference(self.parm.keys())
        if missing:
            raise ValueError(f"Missing run parameters: {sorted(missing)}")

        for key in required:
            value = self.parm[key]
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f'Parameter "{key}" must be a positive integer')

        if self.parm["inactive"] >= self.parm["batches"]:
            raise ValueError('"inactive" must be smaller than "batches"')

        if self.generations_per_batch < 1:
            raise ValueError('"generations_per_batch" must be >= 1')

    def get_settings(self) -> openmc.Settings:
        """Build and return an OpenMC ``Settings`` object.

        Returns
        -------
        openmc.Settings
            Configured settings object without writing XML to disk.
        """
        self.validate()
        settings = openmc.Settings()
        settings.run_mode = self.run_mode
        settings.batches = self.parm["batches"]
        settings.inactive = self.parm["inactive"]
        settings.particles = self.parm["npg"]
        settings.generations_per_batch = self.generations_per_batch
        settings.photon_transport = self.photon_transport
        if self.ext_sources is not None:
            settings.source = self.ext_sources
        return settings
