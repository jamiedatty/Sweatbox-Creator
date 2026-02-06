import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os  # <-- ADD THIS LINE
import sys

class HomePage:
    def __init__(self, parent):
        self.parent = parent
        self.ese_parser = None
        self.sct_parser = None
        self.rwy_parser = None
        self.map_viewer = None
        self.master_controller = "SYS"
        self.aircraft_details_tree = None
        self.controller_tree = None
        
        # Add project root to path for imports
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Now try to import modules
        try:
            from modules.parsers.ese_parser import ESEParser
            from modules.parsers.sct_parser_simple import SCTParser
            from modules.parsers.rwy_parser import RWYParser
            from modules.generators.random_generator import RandomScenarioGenerator
            from modules.exporters.sweatbox_exporter import SweatboxExporter
            from modules.ui.viewers.sweatbox_map import SweatboxMapViewer
            
            self.ESEParser = ESEParser
            self.SCTParser = SCTParser
            self.RWYParser = RWYParser
            self.RandomScenarioGenerator = RandomScenarioGenerator
            self.SweatboxExporter = SweatboxExporter
            self.SweatboxMapViewer = SweatboxMapViewer
            
        except ImportError as e:
            print(f"Import error: {e}")
            print("Creating fallback classes...")
            
            # Create fallback classes
            class FallbackESEParser:
                def __init__(self, *args): 
                    self.positions = []
                def get_positions(self): 
                    return []
            
            class FallbackSCTParser:
                def __init__(self, *args): 
                    self.data = {}
                def parse(self): 
                    pass
                def get_data(self): 
                    return {}
            
            class FallbackRWYParser:
                def __init__(self, *args): 
                    self.runways = []
                    self.ils_data = []
                def parse(self): 
                    pass
                def get_data(self): 
                    return {'runways': [], 'ils_data': []}
            
            class FallbackRandomScenarioGenerator:
                def __init__(self, creator): 
                    self.creator = creator
                def generate_random_scenario(self): 
                    messagebox.showinfo("Info", "Random generator not available")
            
            class FallbackSweatboxExporter:
                def __init__(self, creator): 
                    self.creator = creator
                def export(self, file_path): 
                    return (False, "Exporter not available")
            
            class FallbackSweatboxMapViewer:
                def __init__(self, parent, ese=None, sct=None, rwy=None):
                    self.parent = parent
                    self.aircraft_points = []
                    self.entry_fixes = []
                    self.selected_airport = None
                def load_data(self): 
                    pass
                def redraw_all(self): 
                    pass
                def clear_aircraft(self): 
                    pass
                def add_aircraft(self, aircraft_data): 
                    pass
                def get_entry_fixes(self): 
                    return self.entry_fixes
                def get_selected_airport(self): 
                    return self.selected_airport
                def setup_ui(self): 
                    # Create a simple frame
                    frame = tk.Frame(self.parent, bg='white')
                    frame.pack(fill='both', expand=True)
                    label = tk.Label(frame, text="Map viewer not available", bg='white')
                    label.pack(pady=50)
            
            self.ESEParser = FallbackESEParser
            self.SCTParser = FallbackSCTParser
            self.RWYParser = FallbackRWYParser
            self.RandomScenarioGenerator = FallbackRandomScenarioGenerator
            self.SweatboxExporter = FallbackSweatboxExporter
            self.SweatboxMapViewer = FallbackSweatboxMapViewer
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_container = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - controls
        left_panel = tk.Frame(main_container, bg='#f0f0f0')
        main_container.add(left_panel, minsize=300)
        
        # Center panel - map
        center_panel = tk.Frame(main_container, bg='white')
        main_container.add(center_panel, minsize=600)
        
        # Right panel - details
        right_panel = tk.Frame(main_container, bg='#f0f0f0')
        main_container.add(right_panel, minsize=300)
        
        self.setup_left_panel(left_panel)
        self.setup_center_panel(center_panel)
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, parent):
        # File controls
        file_frame = tk.LabelFrame(parent, text="File Controls", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # ESE file button
        tk.Button(file_frame, text="Load ESE File", command=self.load_ese_file,
                 bg='#3498db', fg='white').pack(fill=tk.X, pady=5)
        
        # SCT file button
        tk.Button(file_frame, text="Load SCT File", command=self.load_sct_file,
                 bg='#2ecc71', fg='white').pack(fill=tk.X, pady=5)
        
        # RWY file button
        tk.Button(file_frame, text="Load RWY File", command=self.load_rwy_file,
                 bg='#e74c3c', fg='white').pack(fill=tk.X, pady=5)
        
        # Master controller input
        tk.Label(file_frame, text="Master Controller:").pack(anchor=tk.W, pady=(10, 0))
        self.master_controller_entry = tk.Entry(file_frame)
        self.master_controller_entry.pack(fill=tk.X, pady=5)
        self.master_controller_entry.insert(0, "SYS")
        
        # Export button
        tk.Button(file_frame, text="Export Sweatbox", command=self.export_sweatbox, 
                 bg='#9b59b6', fg='white').pack(fill=tk.X, pady=(10, 5))
        
        # Refresh map button
        tk.Button(file_frame, text="Refresh Map", command=self.refresh_map,
                 bg='#f39c12', fg='white').pack(fill=tk.X, pady=5)
        
        # Scenario generation
        scenario_frame = tk.LabelFrame(parent, text="Scenario Generation", padx=10, pady=10)
        scenario_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(scenario_frame, text="Generate Random Scenario", 
                 command=self.generate_random_scenario,
                 bg='#1abc9c', fg='white').pack(fill=tk.X, pady=5)
        
        tk.Button(scenario_frame, text="Generate Aircraft at Entry Fixes", 
                 command=self.generate_aircraft_at_entry,
                 bg='#16a085', fg='white').pack(fill=tk.X, pady=5)
        
        tk.Button(scenario_frame, text="Clear All Aircraft", 
                 command=self.clear_all_aircraft,
                 bg='#c0392b', fg='white').pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = tk.Label(parent, text="Ready", bg='#f0f0f0', fg='#666666')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    
    def setup_center_panel(self, parent):
        # Initialize map viewer
        self.map_viewer = self.SweatboxMapViewer(parent, self.ese_parser, self.sct_parser, self.rwy_parser)
    
    def setup_right_panel(self, parent):
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aircraft tab
        aircraft_frame = tk.Frame(notebook)
        notebook.add(aircraft_frame, text="Aircraft")
        self.setup_aircraft_tab(aircraft_frame)
        
        # Controllers tab
        controller_frame = tk.Frame(notebook)
        notebook.add(controller_frame, text="Controllers")
        self.setup_controller_tab(controller_frame)
        
        # Entry fixes tab
        fixes_frame = tk.Frame(notebook)
        notebook.add(fixes_frame, text="Entry Fixes")
        self.setup_fixes_tab(fixes_frame)
        
        # Route editor tab
        route_frame = tk.Frame(notebook)
        notebook.add(route_frame, text="Route Editor")
        self.setup_route_tab(route_frame)
    
    def setup_aircraft_tab(self, parent):
        # Frame for tree and buttons
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for aircraft
        columns = ("Callsign", "Type", "Altitude", "Position", "Route", "Speed", "Heading")
        self.aircraft_details_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.aircraft_details_tree.heading(col, text=col)
            self.aircraft_details_tree.column(col, width=100)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.aircraft_details_tree.yview)
        x_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.aircraft_details_tree.xview)
        self.aircraft_details_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout
        self.aircraft_details_tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Add Aircraft", command=self.add_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Map", command=self.update_aircraft_on_map).pack(side=tk.LEFT, padx=5)
    
    def setup_controller_tab(self, parent):
        # Create treeview for controllers
        columns = ("Callsign", "Frequency", "Type", "Simulated")
        self.controller_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.controller_tree.heading(col, text=col)
            self.controller_tree.column(col, width=100)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.controller_tree.yview)
        self.controller_tree.configure(yscrollcommand=y_scrollbar.set)
        
        self.controller_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Toggle Simulated", command=self.toggle_controller_sim).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", command=self.clear_controllers).pack(side=tk.LEFT, padx=5)
    
    def setup_fixes_tab(self, parent):
        self.fixes_text = tk.Text(parent, wrap=tk.WORD, height=20)
        self.fixes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(parent, command=self.fixes_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fixes_text.config(yscrollcommand=scrollbar.set)
        
        self.fixes_text.insert(tk.END, "Entry fixes will appear here after selecting an airport.")
        self.fixes_text.config(state=tk.DISABLED)
    
    def setup_route_tab(self, parent):
        self.route_text = tk.Text(parent, wrap=tk.WORD, height=20)
        self.route_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(parent, command=self.route_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.route_text.config(yscrollcommand=scrollbar.set)
        
        self.route_text.insert(tk.END, "Route editor will appear here.")
        self.route_text.config(state=tk.NORMAL)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Apply Route to Selected Aircraft", 
                 command=self.apply_route_to_selected).pack(side=tk.LEFT, padx=5)
    
    def load_ese_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ESE File",
            filetypes=[("ESE files", "*.ese"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.ese_parser = self.ESEParser(file_path)
                
                # Clear existing controllers
                if self.controller_tree:
                    for item in self.controller_tree.get_children():
                        self.controller_tree.delete(item)
                
                # Add controllers to tree
                if hasattr(self.ese_parser, 'get_positions'):
                    positions = self.ese_parser.get_positions()
                    for pos in positions:
                        # Skip _FSS and some _CTR positions
                        if '_FSS' in pos.get('callsign', '') or ('_CTR' in pos.get('callsign', '') and not any(x in pos.get('callsign', '') for x in ['FAJA', 'FACA', 'FALE'])):
                            continue
                        
                        self.controller_tree.insert('', 'end', values=(
                            pos.get('callsign', ''),
                            pos.get('frequency', ''),
                            pos.get('type', ''),
                            '✓'  # Default to simulated
                        ))
                    
                    messagebox.showinfo("Success", f"Loaded ESE file: {file_path}\n{len(positions)} positions found.")
                    self.status_label.config(text=f"Loaded ESE: {os.path.basename(file_path)}")
                else:
                    messagebox.showinfo("Info", "ESE parser loaded but get_positions not available")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ESE file: {str(e)}")
    
    def load_sct_file(self):
        file_path = filedialog.askopenfilename(
            title="Select SCT File",
            filetypes=[("SCT files", "*.sct"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.sct_parser = self.SCTParser(file_path)
                self.sct_parser.parse()
                messagebox.showinfo("Success", f"Loaded SCT file: {file_path}")
                
                # Update map viewer
                if self.map_viewer:
                    self.map_viewer.sct_parser = self.sct_parser
                    self.map_viewer.load_data()
                
                self.status_label.config(text=f"Loaded SCT: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load SCT file: {str(e)}")
    
    def load_rwy_file(self):
        file_path = filedialog.askopenfilename(
            title="Select RWY File",
            filetypes=[("RWY files", "*.rwy"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.rwy_parser = self.RWYParser(file_path)
                self.rwy_parser.parse()
                messagebox.showinfo("Success", f"Loaded RWY file: {file_path}")
                
                # Update map viewer
                if self.map_viewer:
                    self.map_viewer.rwy_parser = self.rwy_parser
                    self.map_viewer.load_data()
                
                self.status_label.config(text=f"Loaded RWY: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load RWY file: {str(e)}")
    
    def generate_random_scenario(self):
        if not self.map_viewer:
            messagebox.showwarning("Warning", "Map viewer not available.")
            return
        
        generator = self.RandomScenarioGenerator(self)
        generator.generate_random_scenario()
    
    def generate_aircraft_at_entry(self):
        if not self.map_viewer:
            messagebox.showwarning("Warning", "Map viewer not available.")
            return
        
        entry_fixes = self.map_viewer.get_entry_fixes()
        airport = self.map_viewer.get_selected_airport()
        
        if not entry_fixes or not airport:
            messagebox.showwarning("Warning", "No entry fixes found. Please select an airport first.")
            return
        
        generator = self.RandomScenarioGenerator(self)
        if hasattr(generator, 'generate_aircraft_at_entry_fixes'):
            aircraft_list = generator.generate_aircraft_at_entry_fixes(entry_fixes, airport)
            
            # Add aircraft to tree and map
            for aircraft in aircraft_list:
                self.add_aircraft_from_dict(aircraft)
            
            # Update map
            self.update_aircraft_on_map()
            
            messagebox.showinfo("Success", f"Generated {len(aircraft_list)} aircraft at entry fixes")
            self.status_label.config(text=f"Generated {len(aircraft_list)} aircraft at entry fixes")
        else:
            messagebox.showinfo("Info", "Aircraft generation at entry fixes not available")
    
    def add_aircraft_from_dict(self, aircraft_dict):
        # Add to tree
        values = (
            aircraft_dict.get('callsign', 'N/A'),
            aircraft_dict.get('type', 'N/A'),
            aircraft_dict.get('altitude', 'N/A'),
            aircraft_dict.get('position', 'N/A'),
            aircraft_dict.get('route', ''),
            aircraft_dict.get('speed', '250'),
            aircraft_dict.get('heading', '000')
        )
        self.aircraft_details_tree.insert('', 'end', values=values)
        
        # Add to map
        if self.map_viewer and hasattr(self.map_viewer, 'add_aircraft'):
            self.map_viewer.add_aircraft(aircraft_dict)
    
    def add_aircraft(self):
        # Simple dialog to add aircraft
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Aircraft")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Callsign:").pack(pady=(10, 0))
        callsign_entry = tk.Entry(dialog, width=30)
        callsign_entry.pack(pady=5)
        callsign_entry.insert(0, "SAA123")
        
        tk.Label(dialog, text="Aircraft Type:").pack(pady=(10, 0))
        type_entry = tk.Entry(dialog, width=30)
        type_entry.pack(pady=5)
        type_entry.insert(0, "A320")
        
        tk.Label(dialog, text="Altitude (ft):").pack(pady=(10, 0))
        alt_entry = tk.Entry(dialog, width=30)
        alt_entry.pack(pady=5)
        alt_entry.insert(0, "35000")
        
        tk.Label(dialog, text="Position (lat,lon):").pack(pady=(10, 0))
        pos_entry = tk.Entry(dialog, width=30)
        pos_entry.pack(pady=5)
        pos_entry.insert(0, "-26.145, 28.234")
        
        tk.Label(dialog, text="Route:").pack(pady=(10, 0))
        route_entry = tk.Entry(dialog, width=30)
        route_entry.pack(pady=5)
        route_entry.insert(0, "DCT FAOR")
        
        def save_aircraft():
            values = (
                callsign_entry.get(),
                type_entry.get(),
                f"{alt_entry.get()}ft",
                pos_entry.get(),
                route_entry.get(),
                "250",  # Default speed
                "000"   # Default heading
            )
            self.aircraft_details_tree.insert('', 'end', values=values)
            dialog.destroy()
            self.update_aircraft_on_map()
        
        tk.Button(dialog, text="Add", command=save_aircraft, bg='#2ecc71', fg='white').pack(pady=20)
    
    def edit_aircraft(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to edit.")
            return
        
        item = selected[0]
        values = self.aircraft_details_tree.item(item, 'values')
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Aircraft")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Callsign:").pack(pady=(10, 0))
        callsign_entry = tk.Entry(dialog, width=30)
        callsign_entry.pack(pady=5)
        callsign_entry.insert(0, values[0])
        
        tk.Label(dialog, text="Aircraft Type:").pack(pady=(10, 0))
        type_entry = tk.Entry(dialog, width=30)
        type_entry.pack(pady=5)
        type_entry.insert(0, values[1])
        
        tk.Label(dialog, text="Altitude (ft):").pack(pady=(10, 0))
        alt_entry = tk.Entry(dialog, width=30)
        alt_entry.pack(pady=5)
        alt_entry.insert(0, values[2].replace('ft', ''))
        
        tk.Label(dialog, text="Position (lat,lon):").pack(pady=(10, 0))
        pos_entry = tk.Entry(dialog, width=30)
        pos_entry.pack(pady=5)
        pos_entry.insert(0, values[3])
        
        tk.Label(dialog, text="Route:").pack(pady=(10, 0))
        route_entry = tk.Entry(dialog, width=30)
        route_entry.pack(pady=5)
        route_entry.insert(0, values[4])
        
        tk.Label(dialog, text="Speed:").pack(pady=(10, 0))
        speed_entry = tk.Entry(dialog, width=30)
        speed_entry.pack(pady=5)
        speed_entry.insert(0, values[5] if len(values) > 5 else "250")
        
        tk.Label(dialog, text="Heading:").pack(pady=(10, 0))
        heading_entry = tk.Entry(dialog, width=30)
        heading_entry.pack(pady=5)
        heading_entry.insert(0, values[6] if len(values) > 6 else "000")
        
        def save_changes():
            new_values = (
                callsign_entry.get(),
                type_entry.get(),
                f"{alt_entry.get()}ft",
                pos_entry.get(),
                route_entry.get(),
                speed_entry.get(),
                heading_entry.get()
            )
            self.aircraft_details_tree.item(item, values=new_values)
            dialog.destroy()
            self.update_aircraft_on_map()
        
        tk.Button(dialog, text="Save", command=save_changes, bg='#2ecc71', fg='white').pack(pady=20)
    
    def delete_aircraft(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to delete.")
            return
        
        for item in selected:
            self.aircraft_details_tree.delete(item)
        
        self.update_aircraft_on_map()
        self.status_label.config(text=f"Deleted {len(selected)} aircraft")
    
    def clear_all_aircraft(self):
        for item in self.aircraft_details_tree.get_children():
            self.aircraft_details_tree.delete(item)
        
        if self.map_viewer and hasattr(self.map_viewer, 'clear_aircraft'):
            self.map_viewer.clear_aircraft()
        
        self.status_label.config(text="Cleared all aircraft")
    
    def toggle_controller_sim(self):
        selected = self.controller_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a controller to toggle.")
            return
        
        for item in selected:
            values = list(self.controller_tree.item(item, 'values'))
            if values[3] == '✓':
                values[3] = '✗'
            else:
                values[3] = '✓'
            self.controller_tree.item(item, values=values)
    
    def clear_controllers(self):
        for item in self.controller_tree.get_children():
            self.controller_tree.delete(item)
    
    def apply_route_to_selected(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to apply route to.")
            return
        
        route = self.route_text.get("1.0", tk.END).strip()
        if not route:
            messagebox.showwarning("Warning", "Please enter a route in the Route Editor tab.")
            return
        
        for item in selected:
            values = list(self.aircraft_details_tree.item(item, 'values'))
            if len(values) >= 5:
                values[4] = route
                self.aircraft_details_tree.item(item, values=values)
        
        self.update_aircraft_on_map()
        messagebox.showinfo("Success", f"Applied route to {len(selected)} aircraft")
    
    def export_sweatbox(self):
        if not self.aircraft_details_tree.get_children():
            messagebox.showwarning("Warning", "No aircraft to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Sweatbox File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.master_controller = self.master_controller_entry.get()
                exporter = self.SweatboxExporter(self)
                success, message = exporter.export(file_path)
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.status_label.config(text=f"Exported to {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def refresh_map(self):
        if self.map_viewer and hasattr(self.map_viewer, 'redraw_all'):
            self.map_viewer.redraw_all()
            self.status_label.config(text="Map refreshed")
    
    def update_aircraft_on_map(self):
        """Update aircraft on map from tree data"""
        if not self.map_viewer or not hasattr(self.map_viewer, 'clear_aircraft'):
            return
        
        # Clear existing aircraft from map
        self.map_viewer.clear_aircraft()
        
        # Add all aircraft from tree
        for item in self.aircraft_details_tree.get_children():
            values = self.aircraft_details_tree.item(item, 'values')
            if values and len(values) >= 5:
                callsign, ac_type, altitude, position, route = values[:5]
                
                # Get speed and heading if available
                speed = "250"
                heading = "000"
                if len(values) >= 7:
                    speed = values[5] if values[5] else "250"
                    heading = values[6] if values[6] else "000"
                
                # Create aircraft data dict
                aircraft_data = {
                    'callsign': callsign,
                    'type': ac_type,
                    'altitude': altitude,
                    'position': position,
                    'route': route,
                    'speed': speed,
                    'heading': heading
                }
                
                # Add to map
                if hasattr(self.map_viewer, 'add_aircraft'):
                    self.map_viewer.add_aircraft(aircraft_data)
        
        if hasattr(self.map_viewer, 'redraw_all'):
            self.map_viewer.redraw_all()
        self.status_label.config(text="Updated aircraft on map")
    
    def on_aircraft_position_update(self, callsign, new_position):
        """Handle aircraft position update from map"""
        for item in self.aircraft_details_tree.get_children():
            values = self.aircraft_details_tree.item(item, 'values')
            if values and values[0] == callsign:
                new_values = list(values)
                new_values[3] = new_position
                self.aircraft_details_tree.item(item, values=tuple(new_values))
                break
    
    def get_simulated_controllers(self):
        """Get controllers marked for simulation"""
        controllers = []
        if self.controller_tree:
            for item in self.controller_tree.get_children():
                values = self.controller_tree.item(item, 'values')
                if values and values[3] == '✓':  # Only simulated controllers
                    controllers.append({
                        'callsign': values[0],
                        'frequency': values[1],
                        'type': values[2]
                    })
        return controllers

# For backward compatibility
SweatboxCreatorPage = HomePage