""" Core design for VR1 """
from vr1.lattice_units import lattice_unit_names

# Write an FA lattice, or teh core lattice, or the whole reactor
core_types: list[str] = ['fuel_lattice', 'active_zone', 'reactor']
# Different core designs
core_designs: dict[str, dict] = {

}

class VR1core:
    """ TODO: lattice structure, geometry of the overall reactor, pool, channels
    """
    def __init__(self):
        pass
