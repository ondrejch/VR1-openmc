import openmc
from vr1.materials import vr1_materials
from vr1.lattice_units import surfaces


class Facility:
    """Class that builds VR1 reactor inside of the facility"""
    def __init__(self, materials: vr1_materials) -> None:
        self.materials = materials
        self.cells: dict = {}
        self.surfaces = surfaces

    def name(self) -> str:
        return "VR1 Facility"

    def build(self, lattice = None):  # I would make this require type TestLattice but I want the functionality of an empty facility. Maybe pointless
        if lattice is not None:
            lattice = lattice.model

        self.cells["core.1"]    = openmc.Cell(name="core.1",    fill = lattice,             region=-self.surfaces["CORE.rec"] & +self.surfaces['RCcy.1'] & -self.surfaces["FAZ.2"] & +self.surfaces["H01.sc"])
        self.cells["surf.1"]    = openmc.Cell(name="surf.1",    fill = self.materials.radialchannel, region=-self.surfaces["RCcy.1"] & +self.surfaces["RCcy.2"] & +self.surfaces["RCpy.2"])
        self.cells["water.1"]   = openmc.Cell(name="water.1",   fill = self.materials.water,         region=-self.surfaces["H01.1"] & +self.surfaces["RCcy.1"] & +self.surfaces["RCpy.1"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & ~self.cells["core.1"].region)
        self.cells["water.2"]   = openmc.Cell(name="water.2",   fill = self.materials.water,         region=-self.surfaces["H01.1"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.4"] & +self.surfaces["RCcy.10"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["water.3"]   = openmc.Cell(name="water.3",   fill = self.materials.water,         region=-self.surfaces["H01.1"] & -self.surfaces["RCpy.4"] & +self.surfaces["RCcy.8"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["OUTrk17"]   = openmc.Cell(name="OUTrk17",   fill = self.materials.steelrc,       region=-self.surfaces["RCcy.9"] & +self.surfaces["RCcy.1"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.2"])
        self.cells["OUTrk16"]   = openmc.Cell(name="OUTrk16",   fill = self.materials.steelrc,       region=-self.surfaces["RCcy.10"] & +self.surfaces["RCcy.9"] & -self.surfaces["RCpy.1"] & +self.surfaces["RCpy.4"])
        self.cells["OUTrk18"]   = openmc.Cell(name="OUTrk18",   fill = self.materials.steelrc,       region=-self.surfaces["RCcy.9"] & +self.surfaces["RCcy.2"] & -self.surfaces["RCpy.3"] & +self.surfaces["RCpy.4"])
        self.cells["OUTrk20"]   = openmc.Cell(name="OUTrk20",   fill = self.materials.radialchannel, region=-self.surfaces["RCcy.9"] & +self.surfaces["RCcy.2"] & -self.surfaces["RCpy.2"] & +self.surfaces["RCpy.3"])
        self.cells["OUTrk22"]   = openmc.Cell(name="OUTrk22",   fill = self.materials.steelrc,       region=-self.surfaces["RCcy.8"] & +self.surfaces["RCcy.1"] & -self.surfaces["RCpy.4"] & -self.surfaces["H01.1"])
        self.cells["OUTrk23"]   = openmc.Cell(name="OUTrk23",   fill = self.materials.radialchannel, region=-self.surfaces["RCcy.1"] & +self.surfaces["RCcy.2"] & -self.surfaces["RCpy.4"] & +self.surfaces["RCpy.12"] & +self.surfaces["RCcz.2"])
        self.cells["OUTrk57"]   = openmc.Cell(name="OUTrk57",   fill = self.materials.lead,          region=-self.surfaces["RCpy.10"] & +self.surfaces["RCpy.11"] & +self.surfaces["RCcy.1"] & -self.surfaces["RCcy.11"] & +self.surfaces["RCcz.2"] & +self.surfaces["H01.3"])
        self.cells["OUTrk58"]   = openmc.Cell(name="OUTrk58",   fill = self.materials.lead,          region=-self.surfaces["RCpy.10"] & +self.surfaces["RCpy.11"] & -self.surfaces["RCky.1"] & -self.surfaces["RCcy.14"] & +self.surfaces["RCcy.11"])
        self.cells["OUTrk61P1"] = openmc.Cell(name="OUTrk61P1", fill = self.materials.steelrc,       region=-self.surfaces["RCcz.2"] & +self.surfaces["RCcz.1"] & -self.surfaces["H01.zt"] & +self.surfaces["RCcy.2"])
        self.cells["OUTrk62P1"] = openmc.Cell(name="OUTrk62P1", fill = self.materials.air,           region=-self.surfaces["RCcz.1"] & +self.surfaces["RCcy.2"] & -self.surfaces["H01.zt"])
        self.cells["OUTrk66"]   = openmc.Cell(name="OUTrk66",   fill = self.materials.lead,          region=-self.surfaces["RCcy.14"] & +self.surfaces["RCcy.13"] & -self.surfaces["RCpy.11"] & +self.surfaces["RCpy.12"])
        self.cells["OUTrk67"]   = openmc.Cell(name="OUTrk67",   fill = self.materials.radialchannel, region=-self.surfaces["RCcy.13"] & +self.surfaces["RCcy.1"] & -self.surfaces["RCpy.11"] & +self.surfaces["RCpy.12"])
        self.cells["OUTrk61P2"] = openmc.Cell(name="OUTrk61P2", fill = self.materials.steelrc,       region=-self.surfaces["RCcz.4"] & +self.surfaces["RCcz.3"] & -self.surfaces["H01.zt"] & +self.surfaces["RCcy.12"])
        self.cells["OUTrk62P2"] = openmc.Cell(name="OUTrk62P2", fill = self.materials.air,           region=-self.surfaces["RCcz.3"] & +self.surfaces["RCcy.12"] & -self.surfaces["H01.zt"])
        self.cells["OUTrk90"]   = openmc.Cell(name="OUTrk90",   fill = self.materials.lead,          region=-self.surfaces["RCpy.12"] & -self.surfaces["BOX.rec"] & -self.surfaces["RCcy.14"] & +self.surfaces["RCcy.13"] & +self.surfaces["RCcz.4"])
        self.cells["OUTrk91"]   = openmc.Cell(name="OUTrk91",   fill = self.materials.radialchannel, region=-self.surfaces["RCpy.12"] & -self.surfaces["BOX.rec"] & -self.surfaces["RCcy.13"] & +self.surfaces["RCcy.12"] & +self.surfaces["RCcz.4"])
        self.cells["HO1vsl1"]   = openmc.Cell(name="HO1vsl1",   fill = self.materials.vessel,        region=-self.surfaces["H01.2"] & +self.surfaces["H01.1"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & +self.surfaces["RCcy.1"])
        self.cells["HO1vsl2"]   = openmc.Cell(name="HO1vsl2",   fill = self.materials.air,           region=-self.surfaces["H01.3"] & +self.surfaces["H01.2"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & +self.surfaces["RCcy.1"])
        self.cells["SHIELD1"]   = openmc.Cell(name="SHIELD1",   fill = self.materials.concrete,      region=-self.surfaces["BOX.rec"] & +self.surfaces["H01.3"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & +self.surfaces["RCcy.14"] & +self.surfaces["RCcz.2"] & +self.surfaces["RCcz.4"])
        self.cells["SHIELD2"]   = openmc.Cell(name="SHIELD2",   fill = self.materials.concrete,      region=-self.surfaces["BOX.rec"] & +self.surfaces["H01.3"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"] & -self.surfaces["RCcy.14"] & +self.surfaces["RCky.1"] & +self.surfaces["RCcy.11"] & +self.surfaces["RCcz.2"] & +self.surfaces["RCcz.4"])
        self.cells["OUT.1"]     = openmc.Cell(name="OUT.1",     fill = self.materials.air,           region=+self.surfaces["BOX.rec"] & -self.surfaces["H01.zt"] & +self.surfaces["H01.zd"])
        self.cells["OUT.2"]     = openmc.Cell(name="OUT.2",     fill = self.materials.air,           region=+self.surfaces["H01.zt"])
        self.cells["OUT.3"]     = openmc.Cell(name="OUT.3",     fill = self.materials.air,           region=-self.surfaces["H01.zd"])
        self.cells["V2.1"]      = openmc.Cell(name="V2.1",      fill = self.materials.air,           region=-self.surfaces["RCcy.2"] & +self.surfaces["RCcy.3"] & +self.surfaces["RCpy.9"])
        self.cells["V2.2"]      = openmc.Cell(name="V2.2",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.3"] & +self.surfaces["RCcy.4"] & +self.surfaces["RCcy.6"] & +self.surfaces["RCpy.5"])
        self.cells["V2.3"]      = openmc.Cell(name="V2.3",      fill = self.materials.water,         region=-self.surfaces["RCcy.4"] & +self.surfaces["RCcy.5"] & +self.surfaces["RCpy.5"])
        self.cells["V2.4"]      = openmc.Cell(name="V2.4",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.5"] & +self.surfaces["RCcy.6"] & +self.surfaces["RCpy.5"])
        self.cells["V2.5"]      = openmc.Cell(name="V2.5",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.3"] & +self.surfaces["RCcy.6"] & -self.surfaces["RCpy.5"] & +self.surfaces["RCpy.6"])
        self.cells["V1.1"]      = openmc.Cell(name="V1.1",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.6"] & +self.surfaces["RCcy.7"] & +self.surfaces["RCpy.6"])
        self.cells["V1.2"]      = openmc.Cell(name="V1.2",      fill = self.materials.water,         region=-self.surfaces["RCcy.7"] & +self.surfaces["RCpy.7"])
        self.cells["V1.3"]      = openmc.Cell(name="V1.3",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.3"] & +self.surfaces["RCcy.7"] & -self.surfaces["RCpy.6"] & +self.surfaces["RCpy.7"])
        self.cells["V1.4"]      = openmc.Cell(name="V1.4",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.3"] & +self.surfaces["RCcy.4"] & -self.surfaces["RCpy.7"] & +self.surfaces["RCpy.8"])
        self.cells["V1.5"]      = openmc.Cell(name="V1.5",      fill = self.materials.water,         region=-self.surfaces["RCcy.4"] & -self.surfaces["RCpy.7"] & +self.surfaces["RCpy.8"])
        self.cells["V1.6"]      = openmc.Cell(name="V1.6",      fill = self.materials.radialchannel, region=-self.surfaces["RCcy.3"] & -self.surfaces["RCpy.8"] & +self.surfaces["RCpy.9"])
        self.cells["air.1"]     = openmc.Cell(name="air.1",     fill = self.materials.air,           region=-self.surfaces["RCcy.2"] & -self.surfaces["RCpy.9"] & +self.surfaces["RCpy.12"])
        self.cells["air.2"]     = openmc.Cell(name="air.2",     fill = self.materials.air,           region=-self.surfaces["RCcy.12"] & -self.surfaces["RCpy.12"] & -self.surfaces["BOX.rec"])

        # self.cells["0.w.2"] = openmc.Cell(name="0.w.2", fill = self.materials.water, region=-self.surfaces["ELE.1"] & -self.surfaces["ELE.zp"] & +self.surfaces["GRD.zt"])
        # self.cells["0.w.4"] = openmc.Cell(name="0.w.4", fill = self.materials.water, region=-self.surfaces["ELE.1"] & +self.surfaces["GRD.1"] & +self.surfaces["GRD.xp"] & +self.surfaces["GRD.yp"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.5"] = openmc.Cell(name="0.w.5", fill = self.materials.water, region=-self.surfaces["ELE.1"] & +self.surfaces["GRD.1"] & +self.surfaces["GRD.xp"] & -self.surfaces["GRD.yn"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.6"] = openmc.Cell(name="0.w.6", fill = self.materials.water, region=-self.surfaces["ELE.1"] & +self.surfaces["GRD.1"] & -self.surfaces["GRD.xn"] & +self.surfaces["GRD.yp"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.7"] = openmc.Cell(name="0.w.7", fill = self.materials.water, region=-self.surfaces["ELE.1"] & +self.surfaces["GRD.1"] & -self.surfaces["GRD.xn"] & -self.surfaces["GRD.yn"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.8"] = openmc.Cell(name="0.w.8", fill = self.materials.grid, region=-self.surfaces["GRD.xp"] & +self.surfaces["GRD.xn"] & +self.surfaces["GRD.1"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.9"] = openmc.Cell(name="0.w.9", fill = self.materials.grid, region=-self.surfaces["GRD.yp"] & +self.surfaces["GRD.yn"] & +self.surfaces["GRD.1"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.10"] = openmc.Cell(name="0.w.10", fill = self.materials.grid, region=-self.surfaces["GRD.1"] & +self.surfaces["GRD.2"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.11"] = openmc.Cell(name="0.w.11", fill = self.materials.water, region=-self.surfaces["GRD.2"] & -self.surfaces["GRD.zt"] & +self.surfaces["GRD.zd"])
        # self.cells["0.w.13"] = openmc.Cell(name="0.w.13", fill = self.materials.water, region=-self.surfaces["ELE.1"] & -self.surfaces["GRD.zd"] & +self.surfaces["ELE.zn"])

        return openmc.Universe(name="facility", cells=list(self.cells.values()))
