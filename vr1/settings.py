""" General OpenMC settings """

import os
import openmc
from datetime import datetime

MY_TIME_NOW: str = datetime.isoformat(datetime.now(), "#", "seconds")

class SettingsOpenMC:
    def __init__(self,
                 name: str = 'openmc deck',
                 xs_lib: str = 'endf7.1',
                 xs_xml_root_path: str = '/opt/OpenMC_DATA',
                 tallies: (list, None) = None,
                 plots: (list, None) = None,
                 parm: (dict, None) = None,
                 rotation: float = 0.0,
                 sources: (None, list) = None,
                 power: (None, float) = None
        ):

        self.supported_code: str = "OpenMC"
        self.name = name
        self.my_time_now = MY_TIME_NOW
        self.xs_lib = xs_lib
        self.xs_xml_root_path = xs_xml_root_path
        if xs_lib == 'endf7.1':
            self.xs_xml: str = os.path.join(xs_xml_root_path, 'endfb-vii.1-hdf5/cross_sections2.xml')
        elif xs_lib == 'endf8.0':
            self.xs_xml: str = os.path.join(xs_xml_root_path, 'endfb-viii.0-hdf5/cross_sections.xml')
        else:
            assert ValueError('xs_lib must be endf8.0 or endf7.1')
        self.hostname = os.uname()[1]
        self.power = power  # [W_th]
        self.tallies = tallies
        self.plots = plots
        self.sources = sources
        self.rotation = rotation
        self.generations_per_batch: int = 1

        if parm is None:
            """ npg: Number of particles per generation
                gen: Number of generations
                nsk: Number of skipped generations """
            self.parm = {'npg': 1000, 'gen': 110, 'nsk': 10}
        else:
            self.parm = parm

    def create_source(self,
                      source_lower_left,
                      source_upper_right,
                      source_type='uniform'
        ):
        """
        Create an OpenMC source definition for arbitrary lattice configuration
        
        Parameters:
        - source_lower_left: [x, y, z] lower left corner of source region
        - source_upper_right: [x, y, z] upper right corner of source region  
        - source_type: Type of source distribution ('uniform', 'point')
        """
        source = openmc.IndependentSource()
        
        if source_type == 'uniform':
            # Create uniform source over the specified region
            source.space = openmc.stats.Box(
                lower_left=source_lower_left,
                upper_right=source_upper_right
            )
        elif source_type == 'point':
            # Point source at center of region
            center = [
                (source_lower_left[0] + source_upper_right[0]) / 2,
                (source_lower_left[1] + source_upper_right[1]) / 2,
                (source_lower_left[2] + source_upper_right[2]) / 2
            ]
            source.space = openmc.stats.Point(center)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
            
        # Default energy and angle distributions
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Watt(a=0.988e6, b=2.249e-6)  # U-235 fission spectrum
        
        if self.sources is None:
            self.sources = []
        self.sources.append(source)
        
        return source

    def create_flux_tally(self, tally_name, regions=None, energy_groups=None, spatial_filters=None):
        """
        Create a flux tally for neutron flux measurement
        
        Parameters:
        - tally_name: Name for the tally
        - regions: List of cells, materials, or universes to tally over
        - energy_groups: Energy group structure (default: single group)
        - spatial_filters: Spatial filters like mesh, cell, or surface filters
        
        Returns:
        - OpenMC Tally object
        """
        tally = openmc.Tally(name=tally_name)
        tally.scores = ['flux']
        
        # Add filters based on what's provided
        if regions:
            if isinstance(regions[0], openmc.Cell):
                tally.filters.append(openmc.CellFilter(regions))
            elif isinstance(regions[0], openmc.Material):
                tally.filters.append(openmc.MaterialFilter(regions))
            elif isinstance(regions[0], openmc.Universe):
                tally.filters.append(openmc.UniverseFilter(regions))
        
        if energy_groups:
            tally.filters.append(openmc.EnergyFilter(energy_groups))
        
        if spatial_filters:
            for spatial_filter in spatial_filters:
                tally.filters.append(spatial_filter)
        
        # Initialize tallies list if needed
        if self.tallies is None:
            self.tallies = []
        self.tallies.append(tally)
        
        return tally

    def create_mesh_flux_tally(self, tally_name, mesh_dimension, lower_left, upper_right, energy_groups=None):
        """
        Create a mesh-based flux tally for spatial flux distribution
        
        Parameters:
        - tally_name: Name for the tally
        - mesh_dimension: [nx, ny, nz] mesh divisions
        - lower_left: [x, y, z] lower left corner of mesh
        - upper_right: [x, y, z] upper right corner of mesh
        - energy_groups: Energy group structure (optional)
        
        Returns:
        - OpenMC Tally object
        """
        # Create rectangular mesh
        mesh = openmc.RegularMesh()
        mesh.dimension = mesh_dimension
        mesh.lower_left = lower_left
        mesh.upper_right = upper_right
        
        # Create tally with mesh filter
        tally = openmc.Tally(name=tally_name)
        tally.filters.append(openmc.MeshFilter(mesh))
        tally.scores = ['flux']
        
        if energy_groups:
            tally.filters.append(openmc.EnergyFilter(energy_groups))
        
        # Initialize tallies list if needed
        if self.tallies is None:
            self.tallies = []
        self.tallies.append(tally)
        
        return tally

    def create_fuel_region_flux_tally(self, lattice=None, energy_groups=None):
        """
        Create a flux tally specifically for fuel regions in the lattice
        
        Parameters:
        - lattice: TestLattice object to extract fuel regions from
        - energy_groups: Energy group structure (optional)
        
        Returns:
        - OpenMC Tally object
        """
        if lattice is None:
            raise ValueError("Lattice object required for fuel region tally")
        
        # Create mesh tally over the lattice fuel region
        mesh_dims = [10, 10, 5]  # Default mesh resolution
        tally = self.create_mesh_flux_tally(
            tally_name='fuel_region_flux',
            mesh_dimension=mesh_dims,
            lower_left=lattice.source_lower_left,
            upper_right=lattice.source_upper_right,
            energy_groups=energy_groups
        )
        
        return tally

    def setup_simulation(self, lattice=None, output_path='.', source_type='uniform'):
        """
        Complete simulation setup: create sources from lattice and export settings.xml
        
        This method automatically handles:
        1. Source creation from lattice source region
        2. Settings XML export with all parameters
        
        Parameters:
        - lattice: TestLattice object with source region defined
        - output_path: Directory to write settings.xml
        - source_type: Type of source distribution ('uniform', 'point')
        
        Returns:
        - Path to created settings.xml file
        """
        # Create source from lattice if provided
        if lattice is not None:
            source = self.create_source(
                lattice.source_lower_left,
                lattice.source_upper_right,
                source_type
            )
            print(f"   ✓ {source_type.capitalize()} neutron source created over lattice region")
        
        # Create and export settings.xml
        settings = openmc.Settings()
        
        # Basic settings
        settings.particles = self.parm['npg']
        settings.generations_per_batch = self.generations_per_batch
        settings.batches = self.parm['gen']
        settings.inactive = self.parm['nsk']
        
        # Cross sections
        settings.cross_sections = self.xs_xml
        
        # Sources
        if self.sources:
            settings.source = self.sources
        
        # Temperature handling
        settings.temperature = {'default': 293.15, 'method': 'interpolation'}
        
        # Export settings
        settings_file = os.path.join(output_path, 'settings.xml')
        settings.export_to_xml(settings_file)
        
        # Export tallies if they exist
        if self.tallies:
            tallies = openmc.Tallies(self.tallies)
            tallies_file = os.path.join(output_path, 'tallies.xml')
            tallies.export_to_xml(tallies_file)
            print(f"   ✓ Tallies XML exported to: {tallies_file}")
        
        print(f"   ✓ Settings XML exported to: {settings_file}")
        return settings_file

    def create_settings_xml(self, geometry=None, materials=None, output_path='.'):
        """
        Create settings.xml file for OpenMC simulation
        
        Parameters:
        - geometry: OpenMC geometry object
        - materials: OpenMC materials object
        - output_path: Directory to write settings.xml
        """
        settings = openmc.Settings()
        
        # Basic settings
        settings.particles = self.parm['npg']
        settings.generations_per_batch = self.generations_per_batch
        settings.batches = self.parm['gen']
        settings.inactive = self.parm['nsk']
        
        # Cross sections
        settings.cross_sections = self.xs_xml
        
        # Sources
        if self.sources:
            settings.source = self.sources
        
        # Temperature handling
        settings.temperature = {'default': 293.15, 'method': 'interpolation'}
        
        # Export settings
        settings_file = os.path.join(output_path, 'settings.xml')
        settings.export_to_xml(settings_file)
        
        # Export tallies if they exist
        if self.tallies:
            tallies = openmc.Tallies(self.tallies)
            tallies_file = os.path.join(output_path, 'tallies.xml')
            tallies.export_to_xml(tallies_file)
            print(f"Tallies XML exported to: {tallies_file}")
        
        print(f"Settings XML exported to: {settings_file}")
        return settings_file