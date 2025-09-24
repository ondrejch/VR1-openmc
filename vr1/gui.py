"""GUI frontend for VR1 reactor lattice builder using tkinter"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import copy
from typing import List, Optional


class VR1LatticeBuilder:
    """Interactive GUI for building VR1 reactor lattice configurations"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VR-1 Reactor Lattice Builder")
        self.root.geometry("800x700")
        
        # Valid component types based on lattice_unit_builders
        self.component_types = [
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
            ['0', '1', '2', '3', '4', '5', '6', '7'],
            ['1', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['2', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['3', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['4', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['5', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['6', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['7', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ]
        
        self.current_lattice = copy.deepcopy(self.default_lattice)
        self.buttons = []  # Will store button grid
        
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
        self.buttons = []
        for row in range(8):
            button_row = []
            for col in range(8):
                btn = tk.Button(grid_frame, 
                              width=6, height=3,
                              command=lambda r=row, c=col: self.on_cell_click(r, c),
                              font=('Courier', 10, 'bold'))
                btn.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(btn)
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
            label = ttk.Label(legend_frame, text=legend_text, font=('Courier', 9))
            label.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=8, pady=10)
        
        # Control buttons
        ttk.Button(button_frame, text="Load Default", 
                  command=self.load_default_lattice).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset All to Water", 
                  command=self.reset_to_water).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self.save_configuration).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Load Configuration", 
                  command=self.load_configuration).grid(row=0, column=3, padx=5)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def get_cell_color(self, component: str) -> str:
        """Get display color for component type"""
        color_map = {
            'w': '#E6F3FF',      # Light blue for water
            '8': '#FF6B6B',      # Red for 8-tube FA
            '6': '#4ECDC4',      # Teal for 6-tube FA  
            '4': '#45B7D1',      # Blue for 4-tube FA
            'X': '#96CEB4',      # Green for inserted control rod
            'O': '#FECA57',      # Yellow for removed control rod
            'd': '#DDA0DD',      # Plum for dummy
            'rt': '#DDA0DD',     # Plum for rabbit tube dummy
            'wrc': '#F0F8FF',    # Alice blue for empty water
            'v90': '#FFB347',    # Orange for large channel
            'v56': '#FFCC99',    # Light orange for medium channel  
            'v30': '#FFE5B4',    # Peach for smaller channel
            'v25': '#FFF2CC',    # Light yellow for smaller channel
            'v12': '#FFFACD',    # Lemon for smallest channel
        }
        return color_map.get(component, '#FFFFFF')
    
    def update_button_display(self, row: int, col: int):
        """Update button appearance for given cell"""
        component = self.current_lattice[row][col]
        btn = self.buttons[row][col]
        
        btn.config(text=component, bg=self.get_cell_color(component))
        
        # Add hover tooltip simulation
        description = self.component_descriptions.get(component, component)
        self.status_label.config(text=f"Cell [{row}][{col}]: {description}")
    
    def on_cell_click(self, row: int, col: int):
        """Handle cell button click - cycle through component types"""
        current_component = self.current_lattice[row][col]
        
        # Find current component index
        try:
            current_index = self.component_types.index(current_component)
        except ValueError:
            current_index = 0  # Default to first component if not found
        
        # Cycle to next component
        next_index = (current_index + 1) % len(self.component_types)
        new_component = self.component_types[next_index]
        
        # Update lattice and display
        self.current_lattice[row][col] = new_component
        self.update_button_display(row, col)
    
    def load_default_lattice(self):
        """Load the default lattice template"""
        self.current_lattice = copy.deepcopy(self.default_lattice)
        self.refresh_display()
        self.status_label.config(text="Default lattice loaded")
    
    def reset_to_water(self):
        """Reset all cells to water ('w')"""
        for row in range(8):
            for col in range(8):
                if row == 0:  # Keep row labels
                    self.current_lattice[row][col] = str(col)
                elif col == 0:  # Keep column labels  
                    self.current_lattice[row][col] = str(row)
                else:
                    self.current_lattice[row][col] = 'w'
        self.refresh_display()
        self.status_label.config(text="All cells reset to water")
    
    def refresh_display(self):
        """Refresh the entire grid display"""
        for row in range(8):
            for col in range(8):
                self.update_button_display(row, col)
    
    def save_configuration(self):
        """Save current lattice configuration to custom_lattice.py"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                initialfile="custom_lattice.py"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write('"""Custom VR-1 reactor lattice configuration"""\n\n')
                    f.write('# Generated by VR-1 Lattice Builder GUI\n\n')
                    f.write('CUSTOM_LATTICE = [\n')
                    
                    for row in self.current_lattice:
                        f.write(f'    {row},\n')
                    
                    f.write(']\n\n')
                    f.write('# Usage example:\n')
                    f.write('# from vr1.core import TestLattice\n')
                    f.write('# from custom_lattice import CUSTOM_LATTICE\n')
                    f.write('# my_core = TestLattice(lattice_str=CUSTOM_LATTICE)\n')
                
                self.status_label.config(text=f"Configuration saved to {filename}")
                messagebox.showinfo("Save Successful", f"Lattice configuration saved to:\n{filename}")
        
        except Exception as e:
            self.status_label.config(text=f"Error saving: {str(e)}")
            messagebox.showerror("Save Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_configuration(self):
        """Load lattice configuration from a Python file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                title="Load Lattice Configuration"
            )
            
            if filename:
                # Simple parsing - look for list assignment
                with open(filename, 'r') as f:
                    content = f.read()
                
                # This is a simple approach - in production, you might use ast.literal_eval
                # Look for pattern like CUSTOM_LATTICE = [...] or similar
                import re
                
                # Find list assignment pattern
                pattern = r'(\w+_LATTICE|\w+)\s*=\s*\[(.*?)\]'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    # Try to evaluate the list
                    list_content = '[' + match.group(2) + ']'
                    try:
                        loaded_lattice = eval(list_content)
                        
                        # Validate dimensions
                        if len(loaded_lattice) == 8 and all(len(row) == 8 for row in loaded_lattice):
                            self.current_lattice = loaded_lattice
                            self.refresh_display()
                            self.status_label.config(text=f"Configuration loaded from {filename}")
                            messagebox.showinfo("Load Successful", "Lattice configuration loaded successfully!")
                        else:
                            raise ValueError("Invalid lattice dimensions - must be 8x8")
                    
                    except Exception as eval_error:
                        raise ValueError(f"Could not parse lattice data: {eval_error}")
                else:
                    raise ValueError("Could not find lattice assignment in file")
        
        except Exception as e:
            self.status_label.config(text=f"Error loading: {str(e)}")
            messagebox.showerror("Load Error", f"Failed to load configuration:\n{str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main function to run the lattice builder"""
    app = VR1LatticeBuilder()
    app.run()


if __name__ == "__main__":
    main()