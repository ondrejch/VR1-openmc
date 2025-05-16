""" TODO - this should be a regular class with some intelligent functionality """
import openmc
from vr1.materials import VR1Materials

resolution: int = 5000
materials = VR1Materials()

material_colors: dict = {  # TODO this does not work, no idea why
    materials.water: 'aquamarine',
    materials.cladding: 'silver',
    materials.fuel: 'orangered',
    materials.dummy: 'slategrey'
}


def test_plots() -> openmc.Plots:
    # Everything hardcoded for now
    plot = openmc.Plot()
    plot.filename = 'plot_xy.png'
    plot.width = (100, 100)
    plot.pixels = (resolution, resolution)
    plot.origin = (0, 0, 30)
    plot.color_by = 'cell'
    plot.basis = 'xy'

    plotf = openmc.Plot()
    plotf.filename = 'plot_xy_m.png'
    plotf.width = (100, 100)
    plotf.pixels = (resolution, resolution)
    plotf.origin = (0, 0, 30)
    plotf.color_by = 'material'
    plotf.colors = material_colors
    plotf.basis = 'xy'

    plot1 = openmc.Plot()
    plot1.filename = 'plot_yz.png'
    plot1.width = (100, 200)
    plot1.pixels = (resolution, resolution)
    plot1.origin = (0, 0, 30)
    plot1.color_by = 'cell'
    plot1.basis = 'yz'

    plot1f = openmc.Plot()
    plot1f.filename = 'plot_yz_m.png'
    plot1f.width = (100, 200)
    plot1f.pixels = (resolution, resolution)
    plot1f.origin = (0, 0, 30)
    plot1f.color_by = 'material'
    plot1f.colors = material_colors
    plot1f.basis = 'yz'

    return openmc.Plots([plot, plotf, plot1, plot1f])
