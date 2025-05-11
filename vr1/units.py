import openmc
from materials import VR1Material

rr: dict = {
    "1FT.1": {"widthheight": 6.964, "corner_r": 0.932},
    "1FT.2": {"widthheight": 6.87, "corner_r": 0.885},
    "1FT.3": {"widthheight": 6.73, "corner_r": 0.815},
    "1FT.4": {"widthheight": 6.636, "corner_r": 0.768},
    "2FT.1": {"widthheight": 6.274, "corner_r": 0.852},
    "2FT.2": {"widthheight": 6.18, "corner_r": 0.805},
    "2FT.3": {"widthheight": 6.04, "corner_r": 0.735},
    "2FT.4": {"widthheight": 5.946, "corner_r": 0.688},
    "3FT.1": {"widthheight": 5.584, "corner_r": 0.772},
    "3FT.2": {"widthheight": 5.49, "corner_r": 0.725},
    "3FT.3": {"widthheight": 5.35, "corner_r": 0.655},
    "3FT.4": {"widthheight": 5.256, "corner_r": 0.608},
    "4FT.1": {"widthheight": 4.894, "corner_r": 0.692},
    "4FT.2": {"widthheight": 4.8, "corner_r": 0.645},
    "4FT.3": {"widthheight": 4.66, "corner_r": 0.575},
    "4FT.4": {"widthheight": 4.566, "corner_r": 0.528},
    "5FT.1": {"widthheight": 4.204, "corner_r": 0.612},
    "5FT.2": {"widthheight": 4.11, "corner_r": 0.565},
    "5FT.3": {"widthheight": 3.97, "corner_r": 0.495},
    "5FT.4": {"widthheight": 3.876, "corner_r": 0.448},
    "6FT.1": {"widthheight": 3.514, "corner_r": 0.532},
    "6FT.2": {"widthheight": 3.42, "corner_r": 0.485},
    "6FT.3": {"widthheight": 3.28, "corner_r": 0.415},
    "6FT.4": {"widthheight": 3.186, "corner_r": 0.368},
    "7FT.1": {"widthheight": 2.824, "corner_r": 0.452},
    "7FT.2": {"widthheight": 2.73, "corner_r": 0.405},
    "7FT.3": {"widthheight": 2.59, "corner_r": 0.335},
    "7FT.4": {"widthheight": 2.496, "corner_r": 0.288},
}

cylzs: dict = {
    "8FT.1": 1.067,
    "8FT.2": 1.02,
    "8FT.3": 0.95,
    "8FT.4": 0.903,
}


class IRT4M:
    """ Class that returns IRT4M fuel units """

    def __init__(self, material: VR1Material):
        self.material = material
        self.