import openmc
import matplotlib.pyplot as plt
import os
from vr1.materials import vr1_materials


class PlotManager:
    def __init__(self, model, settings):
        self.model = model
        self.settings = settings
        self.resolution = settings.get('resolution', 1000)
        self.material_colors = {
            vr1_materials.water: 'royalblue',
            vr1_materials.cladding: 'silver',
            vr1_materials.fuel: 'lightcoral',
            vr1_materials.dummy: 'slategrey'
        }
        self.plot_defs = [
            {
                'filename': 'plot_xy',
                'width': (350, 350),
                'basis': 'xy',
                'origin': (0, 0, 0)
            },
            {
                'filename': 'plot_xz',
                'width': (700, 700),
                'basis': 'xz',
                'origin': (0, 0, 0)
            },
            {
                'filename': 'plot_yz',
                'width': (500, 500),
                'basis': 'yz',
                'origin': (0, 0, 0)
            }
        ]

    def create_plots(self):
        plots = []
        for p in self.plot_defs:
            plot = openmc.Plot()
            plot.filename = p['filename']
            plot.width = p['width']
            plot.pixels = (self.resolution, self.resolution)
            plot.color_by = 'material'
            plot.colors = self.material_colors
            plot.show_overlaps = True
            plot.show_outline = True
            plot.basis = p['basis']
            plot.origin = p['origin']
            plots.append(plot)
        plot_file = openmc.Plots(plots)
        plot_file.export_to_xml()
        return plots

    def run_and_display(self, display_plots=True):
        self.create_plots()
        # Generate PNGs using OpenMC's Python API
        openmc.plot_geometry(output=True)
        print("Plots generated!")
        # Optionally display them in Jupyter
        if display_plots:
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            filenames = ['plot_xy.png', 'plot_xz.png', 'plot_yz.png']
            titles = ['XY Plot (z=0)', 'XZ Plot (y=0)', 'YZ Plot (x=0)']
            for ax, fname, title in zip(axes, filenames, titles):
                if os.path.exists(fname):
                    ax.imshow(plt.imread(fname))
                    ax.set_title(title)
                    ax.axis('on')
                else:
                    ax.set_title(f"{title}\n(Not found)")
                    ax.axis('off')
            plt.tight_layout()
            plt.show()