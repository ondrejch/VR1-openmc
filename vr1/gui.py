"""GUI frontend for VR1 reactor lattice builder using tkinter"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ast
import copy
from typing import Iterable

DEFAULT_COMPONENT_TYPES: list[str] = [
    'w',      # Water cell with grid
    '8',      # 8-tube FA
    '6',      # 6-tube FA
    '4',      # 4-tube FA
    'X',      # 6-tube FA with fully inserted control rod
    'O',      # 6-tube FA with fully removed control rod
    'd',      # Empty fuel dummy
    'rt',     # Dummy with rabbit tube
    'wrc',    # Empty water cell
    'v90',    # Vertical channel 90mm
    'v56',    # Vertical channel 56mm
    'v30',    # Vertical channel 30mm
    'v25',    # Vertical channel 25mm
    'v12',    # Vertical channel 12mm
]


def parse_lattice_configuration(
    content: str, allowed_components: Iterable[str] | None = None
) -> list[list[str]]:
    """Parse lattice data from configuration text using safe literal parsing.

    Parameters
    ----------
    content : str
        File content containing either a ``*_LATTICE = [...]`` assignment or a
        bare list expression.
    allowed_components : Iterable[str] | None, optional
        Optional whitelist of valid cell codes.

    Returns
    -------
    list[list[str]]
        Parsed 8x8 lattice configuration.
    """
    module = ast.parse(content, mode='exec')
    lattice = None

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id.upper().endswith("LATTICE")
            for target in node.targets
        ):
            lattice = ast.literal_eval(node.value)
            break

    if lattice is None and len(module.body) == 1 and isinstance(module.body[0], ast.Expr):
        lattice = ast.literal_eval(module.body[0].value)

    if lattice is None:
        raise ValueError("Could not find a lattice assignment in the selected file")
    if not isinstance(lattice, list) or len(lattice) != 8:
        raise ValueError("Invalid lattice dimensions - must be 8x8")

    allowed = set(allowed_components) if allowed_components is not None else None
    normalized: list[list[str]] = []
    for row in lattice:
        if not isinstance(row, list) or len(row) != 8:
            raise ValueError("Invalid lattice dimensions - must be 8x8")
        norm_row: list[str] = []
        for cell in row:
            if not isinstance(cell, str):
                raise ValueError("Lattice entries must be strings")
            if allowed is not None and cell not in allowed:
                raise ValueError(f'Unknown lattice component "{cell}"')
            norm_row.append(cell)
        normalized.append(norm_row)
    return normalized


class VR1LatticeBuilder:
    """Interactive GUI for building VR1 reactor lattice configurations"""
    
    def __init__(self):
        """Create the lattice-builder UI and initialize default state."""
        self.root = tk.Tk()
        self.root.title("VR-1 Reactor Lattice Builder")
        self.root.geometry("800x700")
        
        # Valid component types based on lattice_unit_builders
        self.component_types = list(DEFAULT_COMPONENT_TYPES)
        
        # Component descriptions for tooltip/status
        self.component_descriptions = {
            'w': 'Water cell with grid',
            '8': '8-tube Fuel Assembly',
            '6': '6-tube Fuel Assembly', 
            '4': '4-tube Fuel Assembly',
            'X': '6-tube FA with inserted control rod',
            'O': '6-tube FA with removed control rod',
            'd': 'Empty fuel dummy',
            'rt': 'Dummy with rabbit tube',
            'wrc': 'Empty water cell',
            'v90': 'Vertical channel (90mm)',
            'v56': 'Vertical channel (56mm)',
            'v30': 'Vertical channel (30mm)',
            'v25': 'Vertical channel (25mm)',
            'v12': 'Vertical channel (12mm)',
        }
        
        # Initialize lattice with default template
        self.default_lattice = [
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['w', 'w', '8', '8', '8', '8', 'w', 'w'],
            ['w', 'w', 'v30', '8', '8', 'X', 'v25', 'w'],
            ['w', 'w', 'X', 'X', 'd', 'X', 'w', 'w'],
            ['v56', 'w', '6', 'X', 'X', 'd', 'w', 'v56'],
            ['w', 'w', 'd', 'X', 'v30', '4', 'w', 'w'],
            ['w', 'w', 'd', '8', '8', '8', 'w', 'w'],
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ]

        self.saved_lattice = None   # add this
        self.saved_filename = None  # add this
        self.current_lattice = copy.deepcopy(self.default_lattice)
        self.buttons = []   # store button grid
        self.cell_vars = []    
        self.setup_ui()
        self.load_default_lattice()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="VR-1 Reactor Lattice Builder", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=8, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Click on grid cells to cycle through component types. Grid represents 8x8 reactor lattice.")
        instructions.grid(row=1, column=0, columnspan=8, pady=(0, 10))
        
        # Grid frame
        grid_frame = ttk.LabelFrame(main_frame, text="Reactor Lattice (8x8 Grid)", padding="10")
        grid_frame.grid(row=2, column=0, columnspan=8, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Create 8x8 button grid
        # Replace the existing loop that creates tk.Label widgets
        self.buttons = []
        self.cell_vars = []
        for row in range(8):
            button_row = []
            var_row = []
            for col in range(8):
                var = tk.StringVar(value='w')
                var.trace_add('write', lambda *args, r=row, c=col: self.on_cell_change(r, c))

                entry = tk.Entry(grid_frame, textvariable=var,
                                width=5, font=('Courier', 12, 'bold'),
                                justify='center', relief='solid',
                                bg=self.get_cell_color('w'))
                entry.grid(row=row, column=col, padx=1, pady=1)

                var_row.append(var)
                button_row.append(entry)
            self.cell_vars.append(var_row)
            self.buttons.append(button_row)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=8, pady=10, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready - Click on cells to edit")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Component legend frame
        legend_frame = ttk.LabelFrame(main_frame, text="Component Types", padding="10")
        legend_frame.grid(row=4, column=0, columnspan=8, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Create legend in columns
        for i, component in enumerate(self.component_types):
            row = i // 4
            col = i % 4
            legend_text = f"{component}: {self.component_descriptions.get(component, 'Unknown')}"
            label = ttk.Label(legend_frame, text=legend_text, font=('Courier', 14)) #just changed this
            label.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=8, pady=10)
        
        # Control buttons
        ttk.Button(button_frame, text="Load Default", 
                  command=self.load_default_lattice).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset All to Water", 
                  command=self.reset_to_water).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export Configuration",
                command=self.export_configuration).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Save Configuration",
                command=self.save_configuration).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Load Configuration", 
                  command=self.load_configuration).grid(row=0, column=4, padx=5)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def get_cell_color(self, component: str) -> str:
        """Get display color for component type"""
        if component.startswith('6_'):
            return '#D16413'
        color_map = {
            'w': '#E6F3FF',      # Light blue for water
            '8': '#96CEB4',      # Red for 8-tube FA
            '6': '#4ECDC4',      # Teal for 6-tube FA  
            '4': '#45B7D1',      # Blue for 4-tube FA
            'X': '#FF6B6B',      # Green for inserted control rod
            'O': '#FECA57',      # Yellow for removed control rod
            'd': '#DDA0DD',      # Plum for dummy
            'rt': '#DDA0DD',     # Plum for rabbit tube dummy
            'wrc': '#F0F8FF',    # Alice blue for empty water
            'v90': '#780E74',    # Orange for large channel
            'v56': '#780E74',    # Light orange for medium channel  
            'v30': '#0E7825',    # Peach for smaller channel
            'v25': '#0E7825',    # Light yellow for smaller channel
            'v12': '#0E7825',    # Lemon for smallest channel
        }
        return color_map.get(component, '#FFFFFF')
    
    def update_button_display(self, row: int, col: int):
        component = self.current_lattice[row][col]
        var = self.cell_vars[row][col]
        if var.get() != component:
            var.set(component)
        self.buttons[row][col].config(bg=self.get_cell_color(component))
        description = self.component_descriptions.get(component, component)
        self.status_label.config(text=f"Cell [{row}][{col}]: {description}")
    
    def on_cell_change(self, row: int, col: int):
        """Handle typed input change - validate against known components"""
        new_component = self.cell_vars[row][col].get()
        if new_component in self.component_types or new_component.startswith('6_'):
            self.current_lattice[row][col] = new_component
            self.buttons[row][col].config(bg=self.get_cell_color(new_component))
            description = self.component_descriptions.get(new_component, new_component)
            self.status_label.config(text=f"Cell [{row}][{col}]: {description}")
        else:
            # Invalid input - highlight red until corrected
            self.buttons[row][col].config(bg='#FF9999')
            self.status_label.config(text=f"Unknown component '{new_component}' — see legend below")
    
    def load_default_lattice(self):
        """Load the default lattice template"""
        self.current_lattice = copy.deepcopy(self.default_lattice)
        self.refresh_display()
        self.status_label.config(text="Default lattice loaded")
    
    def reset_to_water(self):
        """Reset all cells to water ('w')"""
        for row in range(8):
            for col in range(8):
                self.current_lattice[row][col] = 'w'
        self.refresh_display()
        self.status_label.config(text="All cells reset to water")
    
    def refresh_display(self):
        """Refresh the entire grid display"""
        for row in range(8):
            for col in range(8):
                self.update_button_display(row, col)
                    
    def export_configuration(self):
        """Export current lattice configuration to a .lat file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".lat",
                filetypes=[("Lattice files", "*.lat"), ("All files", "*.*")],
                initialfile="custom_lattice.lat"
            )

            if filename:
                with open(filename, 'w') as f:
                    f.write('CUSTOM_LATTICE = [\n')
                    for row in self.current_lattice:
                        f.write(f'    {row},\n')
                    f.write(']\n\n')

                self.status_label.config(text=f"Configuration exported to {filename}")
                messagebox.showinfo("Export Successful", f"Lattice configuration exported to:\n{filename}")

        except Exception as e:
            self.status_label.config(text=f"Error exporting: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export configuration:\n{str(e)}")

    def save_configuration(self):
        """Save current lattice to memory and close the GUI"""
        self.saved_lattice = copy.deepcopy(self.current_lattice)
        self.root.destroy()


    
    def load_configuration(self):
        """Load lattice configuration from a Python file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Lattice files", "*.lat"), ("All files", "*.*")],
                title="Load Lattice Configuration"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    content = f.read()
                loaded_lattice = parse_lattice_configuration(
                    content, allowed_components=self.component_types
                )
                self.current_lattice = loaded_lattice
                self.refresh_display()
                self.status_label.config(text=f"Configuration loaded from {filename}")
                messagebox.showinfo("Load Successful", "Lattice configuration loaded successfully!")
        
        except Exception as e:
            self.status_label.config(text=f"Error loading: {str(e)}")
            messagebox.showerror("Load Error", f"Failed to load configuration:\n{str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
        return self.saved_lattice


def main():
    """Main function to run the lattice builder"""
    app = VR1LatticeBuilder()
    app.run()


if __name__ == "__main__":
    main()
