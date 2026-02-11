# sweatbox_map.py
import tkinter as tk
from tkinter import ttk
import tkintermapview
import re
import math
import os
import sys

# Optional Pillow for rotated plane icons
try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
    try:
        from modules.parsers.airport_fetcher import fetch_runways_for_icao
    except Exception:
        fetch_runways_for_icao = None

# Optional web map dependencies
try:
    from flask import Flask
    import folium
    import threading
    import webbrowser
    WEB_MAP_AVAILABLE = True
except Exception:
    WEB_MAP_AVAILABLE = False

# Web map dependencies (Flask and Folium required)
try:
    from flask import Flask
    import folium
    import threading
    import webbrowser
    WEB_MAP_AVAILABLE = True
except Exception:
    WEB_MAP_AVAILABLE = False

# Optional tkinterweb for embedded web view
try:
    import tkinterweb
    TKINTERWEB_AVAILABLE = True
except Exception:
    TKINTERWEB_AVAILABLE = False

class SweatboxMapViewer:
    def __init__(self, parent, ese_parser=None, sct_parser=None, rwy_parser=None, test_mode=False):
        self.parent = parent
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        self.rwy_parser = rwy_parser
        
        # Data storage
        self.aircraft_points = []
        self.entry_fixes = []
        self.selected_airport = None
        self.map_markers = []
        self.map_paths = []
        self.aircraft_markers = []
        self.runway_extensions = []  # Store runway extension lines
        self.loaded_airports = []  # List of airport ICAOs
        self.aircraft_data = []  # Store aircraft data for redraw
        # Toggle verbose debug output - ENABLED BY DEFAULT to diagnose issues
        self.debug = True
        # Plane image cache (heading_quant -> PhotoImage)
        self._plane_image_cache = {}
        # Map of callsign -> marker for efficient updates
        self._aircraft_marker_index = {}
        
        # Aircraft selection
        self.selected_aircraft = None
        self.aircraft_click_bind_id = None
        
        # Runway and airport selection
        self.selected_runways = {}  # Map runway_id -> runway_data
        self.selected_airports = {}  # Map airport_icao -> airport_data
        self.runway_markers = {}  # Map runway_id -> marker for visual highlighting
        self.airport_markers = {}  # Map airport_icao -> marker for visual highlighting
        
        # Initialize map UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the INCREDIBLE map interface with stunning gradients and modern styling"""
        # Create a main frame for the map
        main_frame = tk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True)

        # Create SPECTACULAR gradient control frame with multiple layers
        control_frame = tk.Frame(main_frame, relief='flat', bd=0)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Add MULTIPLE gradient layers for incredible depth
        gradient_bg1 = tk.Frame(control_frame, bg='#667eea', height=6)
        gradient_bg1.pack(fill="x", side=tk.TOP)
        gradient_bg1.pack_propagate(False)

        gradient_bg2 = tk.Frame(control_frame, bg='#764ba2', height=6)
        gradient_bg2.pack(fill="x", side=tk.TOP)
        gradient_bg2.pack_propagate(False)

        gradient_bg3 = tk.Frame(control_frame, bg='#f093fb', height=6)
        gradient_bg3.pack(fill="x", side=tk.TOP)
        gradient_bg3.pack_propagate(False)

        gradient_bg4 = tk.Frame(control_frame, bg='#f5576c', height=6)
        gradient_bg4.pack(fill="x", side=tk.TOP)
        gradient_bg4.pack_propagate(False)

        # Add inner shadow effect
        inner_frame = tk.Frame(control_frame, bg='#ffffff', relief='flat', bd=0)
        inner_frame.pack(fill="x", padx=2, pady=2)

        # Row 1: Airport and Map Controls
        row1_frame = tk.Frame(inner_frame, bg='#f8f9fa')
        row1_frame.pack(fill="x", padx=10, pady=5)

        # Airport selection section
        airport_section = tk.LabelFrame(row1_frame, text="📍 Airport Selection", bg='#f8f9fa', fg='#2c3e50', font=("Arial", 9, "bold"))
        airport_section.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(airport_section, text="Select airport to center map\nand highlight runway extensions:", bg='#f8f9fa', font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 2))
        self.airport_var = tk.StringVar()
        self.airport_combo = ttk.Combobox(airport_section, textvariable=self.airport_var, width=15, state="readonly")
        self.airport_combo.pack(pady=(0, 5))
        self.airport_combo.bind("<<ComboboxSelected>>", self.on_airport_selected)

        # Map controls section
        map_section = tk.LabelFrame(row1_frame, text="🗺️ Map Controls", bg='#f8f9fa', fg='#2c3e50', font=("Arial", 9, "bold"))
        map_section.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(map_section, text="Zoom and view controls:", bg='#f8f9fa', font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 2))

        zoom_frame = tk.Frame(map_section, bg='#f8f9fa')
        zoom_frame.pack(pady=(0, 3))
        tk.Button(zoom_frame, text="🔍+", command=self.zoom_in, width=4, bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=1)
        tk.Button(zoom_frame, text="🔍-", command=self.zoom_out, width=4, bg='#f44336', fg='white').pack(side=tk.LEFT, padx=1)

        tk.Button(map_section, text="📐 Fit All", command=self.fit_to_data, width=10, bg='#2196F3', fg='white').pack(pady=2)
        tk.Button(map_section, text="🔄 Reload", command=self.force_reload_data, width=10, bg='#FF9800', fg='white').pack(pady=(2, 5))

        # Aircraft controls section
        aircraft_section = tk.LabelFrame(row1_frame, text="✈️ Aircraft", bg='#f8f9fa', fg='#2c3e50', font=("Arial", 9, "bold"))
        aircraft_section.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(aircraft_section, text="Selected aircraft status:", bg='#f8f9fa', font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 2))
        self.selected_aircraft_label = tk.Label(aircraft_section, text="None selected", bg='#e3f2fd', fg='#1976d2', font=("Arial", 8, "bold"), relief='sunken', bd=1, padx=5, pady=2)
        self.selected_aircraft_label.pack(fill=tk.X, pady=(0, 3))
        tk.Button(aircraft_section, text="❌ Clear Selection", command=self.clear_aircraft_selection,
                 bg='#ff5722', fg='white', width=15).pack(pady=(0, 5))

        # Row 2: Display Options
        row2_frame = tk.Frame(inner_frame, bg='#f8f9fa')
        row2_frame.pack(fill="x", padx=10, pady=(0, 10))

        display_section = tk.LabelFrame(row2_frame, text="👁️ Display Options", bg='#f8f9fa', fg='#2c3e50', font=("Arial", 9, "bold"))
        display_section.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(display_section, text="Toggle map elements on/off. Runway extensions show 20NM centerline projections for selected runways only (green):", bg='#f8f9fa', font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 5))

        # Create checkboxes in a grid layout for better organization
        checkbox_frame = tk.Frame(display_section, bg='#f8f9fa')
        checkbox_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Initialize variables
        self.show_aircraft_var = tk.BooleanVar(value=True)
        self.show_fixes_var = tk.BooleanVar(value=True)
        self.show_runways_var = tk.BooleanVar(value=True)
        self.show_boundaries_var = tk.BooleanVar(value=False)
        self.show_airports_var = tk.BooleanVar(value=True)
        self.show_runway_extensions_var = tk.BooleanVar(value=False)  # Off by default, on when runway selected
        self.show_controllers_var = tk.BooleanVar(value=False)

        # Row 1 of checkboxes
        cb_row1 = tk.Frame(checkbox_frame, bg='#f8f9fa')
        cb_row1.pack(fill=tk.X, pady=2)
        tk.Checkbutton(cb_row1, text="✈️ Aircraft", variable=self.show_aircraft_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(cb_row1, text="📍 Fixes", variable=self.show_fixes_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(cb_row1, text="🏗️ Runways", variable=self.show_runways_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 15))

        # Row 2 of checkboxes
        cb_row2 = tk.Frame(checkbox_frame, bg='#f8f9fa')
        cb_row2.pack(fill=tk.X, pady=2)
        tk.Checkbutton(cb_row2, text="📏 RWY Extensions", variable=self.show_runway_extensions_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(cb_row2, text="🏢 Airports", variable=self.show_airports_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(cb_row2, text="🚫 Boundaries", variable=self.show_boundaries_var,
                      command=self.redraw_all, bg='#f8f9fa', font=("Arial", 9), state='disabled').pack(side=tk.LEFT, padx=(0, 15))
        
        # Create map widget BELOW controls
        is_test_env = ('PYTEST_CURRENT_TEST' in os.environ) or ('pytest' in sys.modules)
        if is_test_env:
            # Create a lightweight dummy map widget for test environments (no network, no threads)
            class _DummyCanvas:
                def bind(self, *a, **k):
                    pass
                def winfo_width(self):
                    return 800
                def winfo_height(self):
                    return 600
                def coords(self, *a, **k):
                    return None
                def delete(self, *a, **k):
                    pass

            class _DummyWidget:
                def __init__(self, parent, width=800, height=600, corner_radius=0):
                    self.canvas = _DummyCanvas()
                    self.zoom = 3
                def pack(self, *a, **k):
                    pass
                def set_position(self, lat, lon):
                    self._pos = (lat, lon)
                def set_zoom(self, z):
                    self.zoom = z
                def set_marker(self, lat, lon, **kwargs):
                    return type('M', (), {'delete': lambda self: None, 'position': (lat, lon)})()
                def set_path(self, coords, **kwargs):
                    return type('P', (), {'delete': lambda self: None, 'position_list': coords})()
                def set_tile_server(self, *a, **k):
                    pass
                def convert_canvas_coords_to_decimal_coords(self, x, y):
                    return None
                def convert_decimal_to_canvas_coords(self, lat, lon):
                    return (0, 0)

            self.map_widget = _DummyWidget(main_frame, width=800, height=600, corner_radius=0)
        else:
            self.map_widget = tkintermapview.TkinterMapView(main_frame, width=800, height=600, corner_radius=0)
            # Don't pack initially - map will be hidden until toggle button is clicked
            # Set default position (world view)
            self.map_widget.set_position(0.0, 0.0)
            self.map_widget.set_zoom(3)
            # Set tile server to OpenStreetMap
            try:
                self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
            except Exception:
                pass


        
        # Bind double-click for aircraft movement
        self.map_widget.canvas.bind("<Double-Button-1>", self.on_map_double_click)

        # Map pan/zoom handlers
        self._reposition_after_id = None
        # Drag to pan
        self.map_widget.canvas.bind("<ButtonPress-1>", self._on_map_button_press)
        self.map_widget.canvas.bind("<B1-Motion>", self._on_map_drag)
        self.map_widget.canvas.bind("<ButtonRelease-1>", lambda e: self._schedule_aircraft_reposition(delay=50))
        # Mouse wheel to zoom
        try:
            self.map_widget.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        except Exception:
            # Some platforms use Button-4/5
            try:
                self.map_widget.canvas.bind("<Button-4>", self._on_mouse_wheel)
                self.map_widget.canvas.bind("<Button-5>", self._on_mouse_wheel)
            except Exception:
                pass

        # Reposition aircraft after resize
        self.map_widget.canvas.bind("<Configure>", lambda e: self._schedule_aircraft_reposition(delay=50))

        # Create selection info frame with gradient
        selection_frame = tk.Frame(self.parent, bg='#e8f4f8', relief='sunken', bd=1)
        selection_frame.pack(fill="x", padx=10, pady=5)

        # Add gradient to selection frame
        sel_gradient1 = tk.Frame(selection_frame, bg='#a8e6cf', height=3)
        sel_gradient1.pack(fill="x", side=tk.TOP)
        sel_gradient1.pack_propagate(False)

        sel_gradient2 = tk.Frame(selection_frame, bg='#ffd3a5', height=3)
        sel_gradient2.pack(fill="x", side=tk.TOP)
        sel_gradient2.pack_propagate(False)

        # Inner frame for content
        sel_inner = tk.Frame(selection_frame, bg='#e8f4f8')
        sel_inner.pack(fill="x", padx=2, pady=2)

        # Left section: Selection info
        info_frame = tk.Frame(sel_inner, bg='#e8f4f8')
        info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(info_frame, text="Selected Items:", bg='#e8f4f8', font=("Arial", 9, "bold")).pack(side=tk.TOP, anchor=tk.W)
        self.selection_label = tk.Label(info_frame, text="None", bg='#e8f4f8', fg='green', font=("Arial", 9))
        self.selection_label.pack(side=tk.TOP, anchor=tk.W, pady=(2, 0))

        # Right section: Clear button
        button_frame = tk.Frame(sel_inner, bg='#e8f4f8')
        button_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        clear_btn = tk.Button(button_frame, text="Clear All Selections", command=self.clear_runway_airport_selection,
                 bg='#ffcc99', fg='#333333', font=("Arial", 8, "bold"), relief='raised', bd=2)
        clear_btn.pack(side=tk.TOP)

        # Now add tooltips after map_widget is created
        if not is_test_env:
            self._add_tooltips()

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        tooltip = None
        def enter(event):
            nonlocal tooltip
            tooltip = tk.Toplevel(self.parent)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry("+%d+%d" % (event.x_root + 10, event.y_root + 10))
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1, font=('Arial', 8))
            label.pack()
            tooltip.lift()
        def leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _add_tooltips(self):
        """Add tooltips to controls after map widget is created"""
        # Add tooltips to existing widgets
        try:
            # Airport combo tooltip
            self._create_tooltip(self.airport_combo, "Select airport to center map and show runway extensions")
        except:
            pass

        try:
            # Aircraft selection label tooltip
            self._create_tooltip(self.selected_aircraft_label, "Currently selected aircraft (click map markers to select)")
        except:
            pass
    
    def update_airports(self, airports):
        """Update the airport dropdown with extracted airports"""
        self.loaded_airports = airports
        self.airport_combo['values'] = airports
        if airports:
            self.airport_combo.set(airports[0])
            self.selected_airport = airports[0]
    
    def load_data(self):
        """Load data from parsers and display on map"""
        if self.debug:
            print("=" * 50)
            print("DEBUG: Loading data to map...")
        
        # Clear existing map elements
        self.clear_map()
        
        # Track what we're drawing
        items_drawn = 0
        
        # Load data from SCT parser
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            try:
                data = self.sct_parser.get_data()
                if self.debug:
                    print(f"DEBUG: SCT parser has data: {bool(data)}")
                    print(f"DEBUG: Data keys: {list(data.keys())}")
                items_drawn += self.draw_sct_data(data)
            except Exception as e:
                print(f"ERROR drawing SCT data: {e}")
                import traceback
                traceback.print_exc()
        
        # Load data from RWY parser
        if self.rwy_parser and hasattr(self.rwy_parser, 'get_data'):
            try:
                data = self.rwy_parser.get_data()
                print(f"DEBUG: RWY parser has data: {bool(data)}")
                items_drawn += self.draw_rwy_data(data)
            except Exception as e:
                print(f"ERROR drawing RWY data: {e}")
                import traceback
                traceback.print_exc()
        
        # Load data from ESE parser
        if self.ese_parser and hasattr(self.ese_parser, 'get_all_coordinates'):
            try:
                coordinates = self.ese_parser.get_all_coordinates()
                print(f"DEBUG: ESE parser has {len(coordinates)} coordinates")
                items_drawn += self.draw_ese_data(coordinates)
            except Exception as e:
                print(f"ERROR drawing ESE data: {e}")
                import traceback
                traceback.print_exc()
        
        # Draw runway extensions
        if self.show_runway_extensions_var.get():
            items_drawn += self.draw_runway_extensions()
        
        # Redraw aircraft if we have any
        if self.aircraft_data and self.show_aircraft_var.get():
            items_drawn += len(self.aircraft_data)
            self.draw_aircraft()
        
        print(f"DEBUG: Total items drawn: {items_drawn}")
        
        # Auto-fit to data if we have any
        if items_drawn > 0:
            self.fit_to_data()
            if self.debug:
                print("DEBUG: Fitted map to data")
        else:
            if self.debug:
                print("DEBUG: No items to draw - showing default view")
            self.map_widget.set_position(0.0, 0.0)
            self.map_widget.set_zoom(3)
        
        print("=" * 50)
    
    def draw_sct_data(self, data):
        """Draw SCT data on map - returns count of items drawn"""
        items_drawn = 0
        
        # Draw airports - FIXED VERSION
        if 'airports' in data and data['airports'] and self.show_airports_var.get():
            print(f"DEBUG: Drawing {len(data['airports'])} airports")
            for airport in data['airports'][:50]:  # Limit for performance
                try:
                    # SCTParser returns airports as dicts
                    if isinstance(airport, dict):
                        lat = float(airport.get('latitude', 0))
                        lon = float(airport.get('longitude', 0))
                        icao = airport.get('icao', 'N/A')
                    else:
                        # Fallback for other formats
                        continue
                    
                    # Validate coordinates
                    if -90 <= lat <= 90 and -180 <= lon <= 180 and lat != 0 and lon != 0:
                        # Create a closure to capture the current values
                        def make_airport_click_handler(icao, airport_data):
                            def handler(marker):
                                self.on_airport_marker_click(marker, icao, airport_data)
                            return handler
                        
                        marker = self.map_widget.set_marker(
                            lat, lon,
                            text=icao,
                            marker_color_circle="red",
                            marker_color_outside="pink",
                            text_color="red",
                            font=("Arial", 10, "bold"),
                            command=make_airport_click_handler(icao, airport)
                        )
                        if marker:
                            self.map_markers.append(marker)
                            self.airport_markers[icao] = marker
                            items_drawn += 1
                            print(f"  ✓ Airport {icao}: {lat:.4f}, {lon:.4f}")
                    else:
                        print(f"  ✗ Invalid coordinates for airport {icao}: {lat}, {lon}")
                except (ValueError, TypeError) as e:
                    print(f"  ✗ Error drawing airport {airport.get('icao', 'Unknown')}: {e}")
        
        # Draw VORs
        if 'VOR' in data and data['VOR'] and self.show_fixes_var.get():
            for vor in data['VOR'][:50]:  # Limit for performance
                if 'latitude' in vor and 'longitude' in vor:
                    try:
                        lat = float(vor['latitude'])
                        lon = float(vor['longitude'])
                        vor_id = vor.get('id', 'UNK')
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            marker = self.map_widget.set_marker(
                                lat, lon,
                                text=f"VOR:{vor_id}",
                                marker_color_circle="blue",
                                marker_color_outside="lightblue",
                                font=("Arial", 8)
                            )
                            if marker:
                                self.map_markers.append(marker)
                                items_drawn += 1
                    except (ValueError, TypeError) as e:
                        pass
        
        # Draw NDBs
        if 'NDB' in data and data['NDB'] and self.show_fixes_var.get():
            for ndb in data['NDB'][:50]:  # Limit for performance
                if 'latitude' in ndb and 'longitude' in ndb:
                    try:
                        lat = float(ndb['latitude'])
                        lon = float(ndb['longitude'])
                        ndb_id = ndb.get('id', 'UNK')
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            marker = self.map_widget.set_marker(
                                lat, lon,
                                text=f"NDB:{ndb_id}",
                                marker_color_circle="purple",
                                marker_color_outside="lavender",
                                font=("Arial", 8)
                            )
                            if marker:
                                self.map_markers.append(marker)
                                items_drawn += 1
                    except (ValueError, TypeError) as e:
                        pass
        
        # Draw fixes
        if 'fixes' in data and data['fixes'] and self.show_fixes_var.get():
            for fix in data['fixes'][:100]:  # Limit to first 100 fixes for performance
                if 'latitude' in fix and 'longitude' in fix and 'name' in fix:
                    try:
                        lat = float(fix['latitude'])
                        lon = float(fix['longitude'])
                        name = fix['name']
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            marker = self.map_widget.set_marker(
                                lat, lon,
                                text=name,
                                marker_color_circle="green",
                                marker_color_outside="lightgreen",
                                font=("Arial", 7)
                            )
                            if marker:
                                self.map_markers.append(marker)
                                items_drawn += 1
                    except (ValueError, TypeError) as e:
                        pass
        
        # Draw runways from SCT
        if 'runways' in data and data['runways'] and self.show_runways_var.get():
            if self.debug:
                print(f"DEBUG: Drawing {len(data['runways'])} runways from SCT")
                print(f"  show_runways_var value: {self.show_runways_var.get()}")
                if data['runways'] and len(data['runways']) > 0:
                    first = data['runways'][0]
                    print(f"  First runway structure: {first}")
            runway_count = 0
            for runway_idx, runway in enumerate(data['runways']):
                if self.debug and runway_idx < 2:
                    print(f"  Runway {runway_idx}: {runway}")
                if 'coordinates' in runway and runway['coordinates']:
                    coords = []
                    try:
                        for coord_idx, coord in enumerate(runway['coordinates']):
                            if self.debug and runway_idx < 2 and coord_idx == 0:
                                print(f"    First coord of runway {runway_idx}: {coord} (type: {type(coord).__name__})")
                            if hasattr(coord, 'lat') and hasattr(coord, 'lon'):
                                lat = float(coord.lat)
                                lon = float(coord.lon)
                            elif isinstance(coord, dict) and 'lat' in coord and 'lon' in coord:
                                lat = float(coord['lat'])
                                lon = float(coord['lon'])
                            elif isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                lat = float(coord[0])
                                lon = float(coord[1])
                            else:
                                if runway_idx < 2 and self.debug:
                                    print(f"    Runway {runway_idx}: unrecognized coord format: {coord}")
                                continue
                            
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                coords.append((lat, lon))
                            elif runway_idx < 2 and self.debug:
                                print(f"    Runway {runway_idx}: invalid coordinates: {lat}, {lon}")
                        
                        if len(coords) >= 2:
                            if self.debug and runway_idx < 2:
                                print(f"    Runway {runway_idx}: calling set_path with {len(coords)} coords, map_widget type: {type(self.map_widget).__name__}")
                            try:
                                path = self.map_widget.set_path(coords, color="gray", width=3)
                                if path:
                                    runway_id = f"runway_{runway_idx}"
                                    self.map_paths.append(path)
                                    self.runway_markers[runway_id] = {
                                        'path': path,
                                        'runway_idx': runway_idx,
                                        'runway_data': runway,
                                        'coords': coords
                                    }
                                    items_drawn += 1
                                    runway_count += 1
                                    
                                    # Add clickable marker at runway center for selection
                                    if len(coords) >= 1:
                                        center_idx = len(coords) // 2
                                        center_lat, center_lon = coords[center_idx]
                                        
                                        def make_runway_click_handler(rid, rdata):
                                            def handler(marker):
                                                print(f"DEBUG: Runway marker clicked! runway_id={rid}")
                                                self.on_runway_path_click(rid, rdata)
                                            return handler
                                        
                                        runway_marker = self.map_widget.set_marker(
                                            center_lat, center_lon,
                                            text="RWY",
                                            marker_color_circle="lightgray",
                                            marker_color_outside="white",
                                            font=("Arial", 7),
                                            command=make_runway_click_handler(runway_id, runway)
                                        )
                                        if runway_marker:
                                            print(f"DEBUG: Created clickable marker for runway {runway_id} at ({center_lat:.4f}, {center_lon:.4f})")
                                            self.map_markers.append(runway_marker)
                                        else:
                                            print(f"DEBUG: Failed to create marker for runway {runway_id}")
                                    
                                    if runway_idx < 2 and self.debug:
                                        print(f"    [YES] Runway {runway_idx}: drew path with {len(coords)} points")
                                elif runway_idx < 2 and self.debug:
                                    print(f"    [NO] Runway {runway_idx}: set_path returned None")
                            except Exception as path_err:
                                if runway_idx < 2 and self.debug:
                                    print(f"    [EXCEPTION] Runway {runway_idx} set_path failed: {path_err}")
                        elif runway_idx < 2 and self.debug:
                            print(f"    ✗ Runway {runway_idx}: only {len(coords)} valid coords (need 2+)")
                    except (ValueError, TypeError) as e:
                        if runway_idx < 2 and self.debug:
                            print(f"  ✗ Error drawing runway {runway_idx}: {e}")
            if self.debug and runway_count == 0:
                print(f"  ✗ WARNING: Tried to draw {len(data['runways'])} runways but drew 0")
        
        # Do NOT draw any ARTCC/airspace boundaries per user request.
        # Instead, draw basic SID/STAR entry fix markers if available in raw_sections.
        sids = []
        stars = []
        raw = data.get('raw_sections', {}) if data else {}
        if raw:
            sids = raw.get('SIDS', []) + raw.get('SID', [])
            stars = raw.get('STARS', []) + raw.get('STAR', [])

        # Helper to find fix coordinates by name
        fix_index = {}
        for f in data.get('fixes', []) if data else []:
            name = f.get('name') if isinstance(f, dict) else None
            if name:
                try:
                    fix_index[name.upper()] = (float(f.get('latitude')), float(f.get('longitude')))
                except Exception:
                    continue

        def _draw_procedure_markers(lines, label):
            drawn = 0
            for line in lines[:200]:
                # Tokenize and collect an ordered list of unique fixes present in the line
                tokens = re.findall(r"[A-Z0-9_]+", line.upper())
                coords = []
                seen = set()
                for t in tokens:
                    if t in fix_index and t not in seen:
                        lat, lon = fix_index[t]
                        coords.append((lat, lon, t))
                        seen.add(t)

                # Draw a connected path for the procedure if we have at least two fixes
                try:
                    if len(coords) >= 2:
                        path_points = [(lat, lon) for lat, lon, _ in coords]
                        path = self.map_widget.set_path(path_points, color="darkgreen", width=2)
                        if path:
                            self.map_paths.append(path)
                            drawn += 1

                    # Also add small markers/labels for each fix in the procedure
                    for lat, lon, t in coords:
                        try:
                            marker = self.map_widget.set_marker(
                                lat, lon,
                                text=f"{label}:{t}",
                                marker_color_circle="darkgreen",
                                marker_color_outside="lightgreen",
                                font=("Arial", 7)
                            )
                            if marker:
                                self.map_markers.append(marker)
                                drawn += 1
                        except Exception:
                            pass
                except Exception:
                    pass

            return drawn

        if sids:
            items_drawn += _draw_procedure_markers(sids, "SID")
        if stars:
            items_drawn += _draw_procedure_markers(stars, "STAR")

        return items_drawn
    
    def draw_boundaries_fixed(self, boundaries, color, width=1, name="BOUNDARY"):
        """Draw boundary lines on map - FIXED VERSION - returns count of items drawn"""
        items_drawn = 0
        if not boundaries:
            return items_drawn
            
        if self.debug:
            print(f"DEBUG: Drawing boundaries for {name}")
        
        # DEBUG: Show sample boundary structure
        if boundaries and len(boundaries) > 0:
            sample = boundaries[0]
            print(f"DEBUG: Sample boundary structure - keys: {list(sample.keys())}")
            if 'segments' in sample and sample['segments']:
                sample_seg = sample['segments'][0]
                print(f"DEBUG: Sample segment structure - type: {type(sample_seg)}, keys: {list(sample_seg.keys())}")
                print(f"DEBUG: Sample start: {sample_seg.get('start')}")
                print(f"DEBUG: Sample end: {sample_seg.get('end')}")
        
        for boundary_idx, boundary in enumerate(boundaries[:20]):  # Limit to first 20 boundaries
            if boundary_idx == 0:
                print(f"  DEBUG: First boundary full structure: {boundary}")
                print(f"  DEBUG: Has segments key: {'segments' in boundary}")
                if 'segments' in boundary:
                    print(f"  DEBUG: Segments value: {boundary['segments']}")
                    print(f"  DEBUG: Segments length: {len(boundary['segments']) if boundary['segments'] else 'None/Empty'}")
            
            if 'segments' in boundary and boundary['segments']:
                print(f"  Boundary '{boundary.get('name', f'#{boundary_idx}')}': {len(boundary['segments'])} segments")
                
                for segment_idx, segment in enumerate(boundary['segments'][:200]):  # Limit segments
                    try:
                        # Handle the SCTParser format
                        if 'start' in segment and 'end' in segment:
                            start = segment['start']
                            end = segment['end']
                            
                            # Extract coordinates from SCTParser's dict format
                            if isinstance(start, dict):
                                # SCTParser format: {'lat': 12.34, 'lon': 56.78}
                                lat1 = float(start.get('lat', 0))
                                lon1 = float(start.get('lon', 0))
                            elif isinstance(start, (list, tuple)) and len(start) >= 2:
                                lat1 = float(start[0])
                                lon1 = float(start[1])
                            else:
                                print(f"    ✗ Invalid start format: {type(start)}")
                                continue
                                
                            if isinstance(end, dict):
                                # SCTParser format: {'lat': 12.35, 'lon': 56.79}
                                lat2 = float(end.get('lat', 0))
                                lon2 = float(end.get('lon', 0))
                            elif isinstance(end, (list, tuple)) and len(end) >= 2:
                                lat2 = float(end[0])
                                lon2 = float(end[1])
                            else:
                                print(f"    ✗ Invalid end format: {type(end)}")
                                continue
                            
                            # Validate coordinates
                            if (-90 <= lat1 <= 90 and -180 <= lon1 <= 180 and 
                                -90 <= lat2 <= 90 and -180 <= lon2 <= 180 and
                                (lat1 != 0 or lon1 != 0) and (lat2 != 0 or lon2 != 0)):
                                
                                # Draw the segment
                                path = self.map_widget.set_path(
                                    [(lat1, lon1), (lat2, lon2)],
                                    color=color,
                                    width=width
                                )
                                if path:
                                    self.map_paths.append(path)
                                    items_drawn += 1
                                    
                                    # Debug first few segments
                                    if segment_idx < 3:
                                        print(f"    Segment {segment_idx}: ({lat1:.4f}, {lon1:.4f}) to ({lat2:.4f}, {lon2:.4f})")
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"    ✗ Error in segment {segment_idx}: {e}")
                        continue
        
        print(f"  ✓ Drawn {items_drawn} boundary segments for {name}")
        return items_drawn
    
    def draw_rwy_data(self, data):
        """Draw RWY data on map - returns count of items drawn"""
        items_drawn = 0
        
        # Draw runways
        if 'runways' in data and data['runways'] and self.show_runways_var.get():
            if self.debug:
                print(f"DEBUG: Drawing {len(data['runways'])} runways from RWY")
            for runway in data['runways']:
                if 'coordinates' in runway and runway['coordinates']:
                    coords = []
                    try:
                        for coord in runway['coordinates']:
                            if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                lat = float(coord[0])
                                lon = float(coord[1])
                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    coords.append((lat, lon))
                        
                        if len(coords) >= 2:
                            path = self.map_widget.set_path(coords, color="orange", width=3)
                            if path:
                                self.map_paths.append(path)
                                items_drawn += 1
                    except (ValueError, TypeError) as e:
                        print(f"  ✗ Error drawing RWY runway: {e}")
        
        # Draw ILS
        if 'ils_data' in data and data['ils_data'] and self.show_runways_var.get():
            if self.debug:
                print(f"DEBUG: Drawing {len(data['ils_data'])} ILS")
            for ils in data['ils_data']:
                if 'localizer' in ils and 'glideslope' in ils:
                    localizer = ils['localizer']
                    glideslope = ils['glideslope']
                    if len(localizer) >= 2 and len(glideslope) >= 2:
                        try:
                            lat1 = float(localizer[0])
                            lon1 = float(localizer[1])
                            lat2 = float(glideslope[0])
                            lon2 = float(glideslope[1])
                            
                            if (-90 <= lat1 <= 90 and -180 <= lon1 <= 180 and 
                                -90 <= lat2 <= 90 and -180 <= lon2 <= 180):
                                # Draw ILS localizer line
                                path = self.map_widget.set_path(
                                    [(lat1, lon1), (lat2, lon2)],
                                    color="magenta",
                                    width=2
                                )
                                if path:
                                    self.map_paths.append(path)
                                    items_drawn += 1
                                
                                # Mark ILS position
                                marker = self.map_widget.set_marker(
                                    lat1, lon1,
                                    text=f"ILS:{ils.get('name', '')}",
                                    marker_color_circle="magenta",
                                    font=("Arial", 8)
                                )
                                if marker:
                                    self.map_markers.append(marker)
                                    items_drawn += 1
                        except (ValueError, TypeError) as e:
                            print(f"  ✗ Error drawing ILS {ils.get('name', 'Unknown')}: {e}")
        
        return items_drawn
    
    def draw_ese_data(self, coordinates):
        """Draw ESE data on map - returns count of items drawn"""
        items_drawn = 0

        # Do not draw controllers by default; they should only appear in the controller list
        try:
            if not getattr(self, 'show_controllers_var', tk.BooleanVar(value=False)).get():
                if self.debug:
                    print("DEBUG: Skipping drawing ESE/controller positions (disabled)")
                return 0
        except Exception:
            return 0

        if not coordinates:
            return items_drawn

        if self.debug:
            print(f"DEBUG: Drawing {len(coordinates)} ESE coordinates")
        for coord in coordinates[:100]:  # Limit to first 100
            if 'lat' in coord and 'lon' in coord:
                try:
                    lat = float(coord['lat'])
                    lon = float(coord['lon'])
                    name = coord.get('name', 'POS')

                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        marker = self.map_widget.set_marker(
                            lat, lon,
                            text=name,
                            marker_color_circle="yellow",
                            marker_color_outside="orange",
                            font=("Arial", 8)
                        )
                        if marker:
                            self.map_markers.append(marker)
                            items_drawn += 1
                except (ValueError, TypeError) as e:
                    pass

        return items_drawn

    def highlight_airports(self, icao_list):
        """Place markers for a list of ICAO codes using 3-tier fallback strategy:
        
        Tier 1: SCT data (red marker)
        Tier 2: ESE controller positions (orange marker)
        Tier 3: OurAirports API (blue marker)
        """
        if not icao_list:
            return 0

        drawn = 0
        if not hasattr(self, '_highlighted_airport_markers'):
            self._highlighted_airport_markers = []

        # Remove previous highlighted markers
        try:
            for hm in list(self._highlighted_airport_markers):
                try:
                    hm.delete()
                except Exception:
                    pass
            self._highlighted_airport_markers = []
        except Exception:
            pass

        icao_set = set([i.upper() for i in icao_list if i])
        
        if self.debug:
            print(f"[HIGHLIGHT] Highlighting {len(icao_set)} airports")

        # TIER 1: Try to find airports in SCT
        found_in_sct = set()
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            try:
                data = self.sct_parser.get_data()
                if data and 'airports' in data and data['airports']:
                    if self.debug:
                        print(f"[HIGHLIGHT] SCT has {len(data.get('airports', []))} airports")
                    
                    for airport in data.get('airports', []):
                        icao = (airport.get('icao') or '').upper()
                        if icao in icao_set:
                            try:
                                lat = float(airport.get('latitude'))
                                lon = float(airport.get('longitude'))
                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    marker = self.map_widget.set_marker(
                                        lat, lon,
                                        text=icao,
                                        marker_color_circle="red",
                                        marker_color_outside="pink",
                                        text_color="red",
                                        font=("Arial", 10, "bold")
                                    )
                                    if marker:
                                        self._highlighted_airport_markers.append(marker)
                                        drawn += 1
                                        found_in_sct.add(icao)
                                        if self.debug:
                                            print(f"  [TIER1] Found {icao} in SCT at {lat:.4f}, {lon:.4f}")
                            except (ValueError, TypeError):
                                pass
            except Exception as e:
                if self.debug:
                    print(f"[HIGHLIGHT] Error searching SCT: {e}")

        # TIER 2: For airports not found in SCT, try to find them in ESE controller positions
        found_in_ese = set()
        not_found_in_sct = icao_set - found_in_sct
        if not_found_in_sct:
            if self.debug:
                print(f"[HIGHLIGHT] {len(not_found_in_sct)} airports not in SCT, checking ESE positions: {not_found_in_sct}")
            
            if not self.ese_parser:
                if self.debug:
                    print(f"[HIGHLIGHT] ESE parser not available (None)")
            else:
                try:
                    # Get all controller positions from ESE
                    positions = []
                    if hasattr(self.ese_parser, 'get_positions'):
                        positions = self.ese_parser.get_positions()
                    
                    if self.debug:
                        print(f"[HIGHLIGHT] ESE has {len(positions)} controller positions")
                        if len(positions) <= 20:
                            # Show all callsigns for debugging
                            for pos in positions:
                                cs = (pos.get('callsign') or '').strip().upper()
                                lat = pos.get('latitude')
                                lon = pos.get('longitude')
                                print(f"  [DEBUG] ESE controller: {cs} @ ({lat}, {lon})")
                    
                    # Match controllers to airports
                    for icao in not_found_in_sct:
                        found_airport = False
                        # Find a controller whose callsign starts with this ICAO
                        for pos in positions:
                            callsign = (pos.get('callsign') or '').strip().upper()
                            # Check if controller callsign starts with the airport ICAO
                            if callsign.startswith(icao):
                                try:
                                    lat = float(pos.get('latitude', 0))
                                    lon = float(pos.get('longitude', 0))
                                    if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat != 0 or lon != 0):
                                        marker = self.map_widget.set_marker(
                                            lat, lon,
                                            text=icao,
                                            marker_color_circle="orange",
                                            marker_color_outside="lightyellow",
                                            text_color="darkorange",
                                            font=("Arial", 10, "bold")
                                        )
                                        if marker:
                                            self._highlighted_airport_markers.append(marker)
                                            drawn += 1
                                            found_airport = True
                                            found_in_ese.add(icao)
                                            if self.debug:
                                                print(f"  [TIER2] Found {icao} in ESE via {callsign} at {lat:.4f}, {lon:.4f}")
                                            break  # Found this airport, move to next one
                                except (ValueError, TypeError) as e:
                                    if self.debug:
                                        print(f"  [ERR] Error parsing {icao} coords: {e}")
                                    pass
                        
                        if not found_airport and self.debug:
                            print(f"  [TIER2] {icao} not found in ESE")
                except Exception as e:
                    if self.debug:
                        print(f"[HIGHLIGHT] Error searching ESE: {e}")

        # TIER 3: For airports still not found, try OurAirports API
        not_found_in_ese = (not_found_in_sct - found_in_ese)
        if not_found_in_ese:
            if self.debug:
                print(f"[HIGHLIGHT] {len(not_found_in_ese)} airports not in ESE, checking OurAirports API: {not_found_in_ese}")
            
            try:
                from modules.parsers.airport_fetcher import fetch_airport_coordinates
                
                for icao in not_found_in_ese:
                    coords = fetch_airport_coordinates(icao)
                    if coords and coords.get('latitude') and coords.get('longitude'):
                        try:
                            lat = float(coords['latitude'])
                            lon = float(coords['longitude'])
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                marker = self.map_widget.set_marker(
                                    lat, lon,
                                    text=icao,
                                    marker_color_circle="blue",
                                    marker_color_outside="lightblue",
                                    text_color="darkblue",
                                    font=("Arial", 10, "bold")
                                )
                                if marker:
                                    self._highlighted_airport_markers.append(marker)
                                    drawn += 1
                                    if self.debug:
                                        print(f"  [TIER3] Found {icao} from OurAirports at {lat:.4f}, {lon:.4f}")
                        except (ValueError, TypeError) as e:
                            if self.debug:
                                print(f"  [ERR] Error adding {icao} from API: {e}")
                    else:
                        if self.debug:
                            print(f"  [TIER3] {icao} not found in OurAirports API")
            except Exception as e:
                if self.debug:
                    print(f"[HIGHLIGHT] Error accessing OurAirports API: {e}")

        if self.debug:
            print(f"[HIGHLIGHT] Highlighted {drawn} total airports")

        # Optionally fit to newly highlighted airports
        if drawn:
            try:
                self.fit_to_data()
            except Exception:
                pass

        return drawn
    
    def draw_runway_extensions(self):
        """Draw 20NM extensions on both ends of selected runways only
        Selected runway extensions display in green with thick lines for better visibility"""
        items_drawn = 0

        print(f"DEBUG: draw_runway_extensions called")
        print(f"DEBUG: show_runway_extensions_var = {self.show_runway_extensions_var.get()}")
        print(f"DEBUG: selected_runways = {list(self.selected_runways.keys())}")

        # Clear existing extensions
        for extension in self.runway_extensions:
            try:
                extension.delete()
            except:
                pass
        self.runway_extensions = []

        # Only draw extensions if enabled AND there are selected runways
        if not self.show_runway_extensions_var.get() or not self.selected_runways:
            print("DEBUG: Runway extensions disabled or no runways selected - skipping extension drawing")
            return items_drawn

        print(f"DEBUG: Drawing green extensions for {len(self.selected_runways)} selected runways")

        # Draw extensions for selected runways only
        for runway_id, runway_data in self.selected_runways.items():
            try:
                # Get coordinates from runway data
                coords = None
                if isinstance(runway_data, dict) and 'coordinates' in runway_data:
                    coords = runway_data['coordinates']
                elif hasattr(runway_data, 'coordinates'):
                    coords = runway_data.coordinates
                else:
                    # Try to find runway by ID in SCT data
                    if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
                        data = self.sct_parser.get_data()
                        if data and 'runways' in data:
                            for rwy_idx, rwy in enumerate(data['runways']):
                                if f"runway_{rwy_idx}" == runway_id:
                                    if 'coordinates' in rwy and rwy['coordinates']:
                                        coords = []
                                        for coord in rwy['coordinates']:
                                            if hasattr(coord, 'lat') and hasattr(coord, 'lon'):
                                                lat = float(coord.lat)
                                                lon = float(coord.lon)
                                            elif isinstance(coord, dict) and 'lat' in coord and 'lon' in coord:
                                                lat = float(coord['lat'])
                                                lon = float(coord['lon'])
                                            elif isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                                lat = float(coord[0])
                                                lon = float(coord[1])
                                            else:
                                                continue
                                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                                coords.append((lat, lon))
                                    break

                if not coords or len(coords) < 2:
                    print(f"DEBUG: No valid coordinates found for runway {runway_id}")
                    continue

                # Calculate runway direction vector
                start_lat, start_lon = coords[0]
                end_lat, end_lon = coords[-1]

                # Calculate bearing
                bearing = self.calculate_bearing(start_lat, start_lon, end_lat, end_lon)
                reverse_bearing = (bearing + 180) % 360

                # Calculate extension points (20NM = ~37km)
                extension_distance = 20 * 1852  # Convert NM to meters

                # Extension from start point (opposite direction)
                ext_start = self.calculate_destination_point(
                    start_lat, start_lon, reverse_bearing, extension_distance
                )

                # Extension from end point
                ext_end = self.calculate_destination_point(
                    end_lat, end_lon, bearing, extension_distance
                )

                # Draw extension lines in GREEN for selected runways
                if ext_start and ext_end:
                    print(f"DEBUG: Drawing green extensions for selected runway {runway_id}")

                    # Draw extension from start (green, thick)
                    try:
                        path1 = self.map_widget.set_path(
                            [coords[0], ext_start],
                            color="green",
                            width=6  # Thick for visibility
                        )
                        if path1:
                            self.runway_extensions.append(path1)
                            self.map_paths.append(path1)
                            items_drawn += 1
                    except Exception as e:
                        print(f"  ✗ Error drawing start extension: {e}")

                    # Draw extension from end (green, thick)
                    try:
                        path2 = self.map_widget.set_path(
                            [coords[-1], ext_end],
                            color="green",
                            width=6  # Thick for visibility
                        )
                        if path2:
                            self.runway_extensions.append(path2)
                            self.map_paths.append(path2)
                            items_drawn += 1
                    except Exception as e:
                        print(f"  ✗ Error drawing end extension: {e}")
                else:
                    print(f"DEBUG: ext_start or ext_end is None for {runway_id}")

            except Exception as e:
                print(f"  ✗ Error drawing runway extension for {runway_id}: {e}")

        print(f"DEBUG: draw_runway_extensions returning with {items_drawn} items drawn")

        return items_drawn
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing between two points in degrees"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon_diff_rad = math.radians(lon2 - lon1)
        
        x = math.sin(lon_diff_rad) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff_rad)
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    def calculate_destination_point(self, lat, lon, bearing, distance):
        """Calculate destination point given start point, bearing and distance in meters"""
        R = 6371000  # Earth's radius in meters
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        lat2_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance / R) +
            math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad)
        )
        
        lon2_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
            math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat2_rad)
        )
        
        return (math.degrees(lat2_rad), math.degrees(lon2_rad))
    
    def on_airport_selected(self, event):
        """Handle airport selection"""
        self.selected_airport = self.airport_var.get()
        print(f"DEBUG: Selected airport: {self.selected_airport}")

        # Find and center on selected airport
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            data = self.sct_parser.get_data()
            if 'airports' in data:
                for airport in data['airports']:
                    if airport.get('icao') == self.selected_airport:
                        try:
                            lat = float(airport['latitude'])
                            lon = float(airport['longitude'])
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                self.map_widget.set_position(lat, lon)
                                self.map_widget.set_zoom(10)
                                print(f"  ✓ Centered on {self.selected_airport} at {lat}, {lon}")
                                break
                            else:
                                print(f"  ✗ Invalid coordinates for {self.selected_airport}: {lat}, {lon}")
                        except (ValueError, TypeError) as e:
                            print(f"  ✗ Error centering on airport: {e}")

        # Turn on runway extensions for this airport
        if self.selected_airport:
            self.show_runway_extensions_var.set(True)
            print(f"DEBUG: Turned on runway extensions for {self.selected_airport}")

            # Select all runways for this airport
            self.selected_runways = {}
            for runway_id, runway_info in self.runway_markers.items():
                if isinstance(runway_info, dict) and 'runway_data' in runway_info:
                    self.selected_runways[runway_id] = runway_info['runway_data']
            print(f"DEBUG: Selected {len(self.selected_runways)} runways for airport {self.selected_airport}")

        # Attempt to load runway data for this airport
        try:
            self.fetch_runway_data_for_airport(self.selected_airport)
        except Exception:
            pass

        # Redraw runway extensions for this airport
        try:
            print(f"DEBUG: Drawing runway extensions for {self.selected_airport}")
            self.draw_runway_extensions()
        except Exception as e:
            print(f"DEBUG: Error drawing runway extensions: {e}")
    
    def force_reload_data(self):
        """Force reload all data - useful for debugging"""
        if self.debug:
            print("DEBUG: Force reloading all data")
        
        # Clear all stored data
        self.aircraft_points = []
        self.entry_fixes = []
        self.map_markers = []
        self.map_paths = []
        self.aircraft_markers = []
        self.runway_extensions = []
        self.aircraft_data = []
        
        # Clear the map
        self.clear_map()
        
        # Re-parse and load data
        if self.sct_parser:
            try:
                # Force re-parse if the parser supports it
                if hasattr(self.sct_parser, 'parse'):
                    data = self.sct_parser.parse()
                    print(f"DEBUG: Re-parsed SCT data")
                else:
                    data = self.sct_parser.get_data()
                    print(f"DEBUG: Got SCT data from cache")
            except Exception as e:
                print(f"ERROR re-parsing SCT: {e}")
                data = {}
        
        # Redraw
        self.load_data()
    
    def clear_map(self):
        """Clear all map markers and paths"""
        # Clear markers
        for marker in self.map_markers:
            try:
                marker.delete()
            except:
                pass
        self.map_markers = []

        # Clear paths
        for path in self.map_paths:
            try:
                path.delete()
            except:
                pass
        self.map_paths = []

        # Clear aircraft markers and index (but keep aircraft data)
        for aircraft_marker in self.aircraft_markers:
            try:
                aircraft_marker.delete()
            except:
                pass
        self.aircraft_markers = []
        self._aircraft_marker_index = {}  # Clear the index since markers are deleted

        # Clear runway extensions
        for extension in self.runway_extensions:
            try:
                extension.delete()
            except:
                pass
        self.runway_extensions = []
    
    def create_plane_icon(self, heading):
        """Create a plane icon polygon rotated to the specified heading"""
        # Define plane shape (pointing north at 0 degrees)
        # Coordinates are relative to center: (x, y) where up is north
        plane_shape = [
            (0, -10),     # Nose
            (4, 0),       # Right wing tip
            (2, 0),       # Right wing inner
            (2, 8),       # Right tail
            (3, 10),      # Right tail tip
            (0, 8),       # Center tail
            (-3, 10),     # Left tail tip
            (-2, 8),      # Left tail
            (-2, 0),      # Left wing inner
            (-4, 0),      # Left wing tip
            (0, -10)      # Back to nose (close polygon)
        ]
        
        # Rotate the shape to match heading
        # Heading is in degrees (0 = North, 90 = East, 180 = South, 270 = West)
        import math
        heading_rad = math.radians(heading)
        cos_h = math.cos(heading_rad)
        sin_h = math.sin(heading_rad)
        
        rotated_shape = []
        for x, y in plane_shape:
            # Rotate point around origin
            new_x = x * cos_h - y * sin_h
            new_y = x * sin_h + y * cos_h
            rotated_shape.append((new_x, new_y))
        
        return rotated_shape

    def _get_plane_photoimage(self, heading, size=32, color="#0000FF"):
        """Return a Tk PhotoImage of a simple plane rotated to `heading` degrees.
        Uses Pillow when available and caches results.
        """
        key = (int(round(heading / 5.0) * 5) % 360, size, color)
        if key in self._plane_image_cache:
            return self._plane_image_cache[key]

        if not PIL_AVAILABLE:
            return None

        try:
            # Create a transparent image
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Simple triangle-like plane pointing up
            cx = size / 2
            cy = size / 2
            scale = size / 3.0
            points = [
                (cx, cy - scale),
                (cx + scale * 0.5, cy + scale * 0.6),
                (cx, cy + scale * 0.2),
                (cx - scale * 0.5, cy + scale * 0.6),
            ]

            # Draw filled plane
            draw.polygon(points, fill=color)

            # Rotate so 0 = North
            rotated = img.rotate(-heading, resample=Image.BICUBIC, expand=True)

            # Trim or paste into fixed-size canvas
            final = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            rx, ry = rotated.size
            final.paste(rotated, ((size - rx) // 2, (size - ry) // 2), rotated)

            photo = ImageTk.PhotoImage(final)
            # Cache and return
            self._plane_image_cache[key] = photo
            return photo
        except Exception:
            return None
    
    def clear_aircraft(self):
        """Clear only aircraft markers and data"""
        # Remove canvas markers and other indexed markers
        for cs, obj in list(self._aircraft_marker_index.items()):
            try:
                if isinstance(obj, dict) and 'canvas_id' in obj:
                    # Delete canvas items
                    self._safe_delete_canvas_items([obj['canvas_id'], obj.get('bg_id')])
                else:
                    try:
                        obj.delete()
                    except:
                        pass
            except Exception:
                pass
        self._aircraft_marker_index = {}
        self.aircraft_markers = []
        self.aircraft_data = []
        self.clear_aircraft_selection()
    
    def add_aircraft(self, aircraft_data):
        """Add aircraft to map and store data"""
        # Validate aircraft data
        if not aircraft_data:
            return
        
        # Ensure position is a string and valid
        if 'position' not in aircraft_data or not aircraft_data['position']:
            print(f"WARNING: Aircraft {aircraft_data.get('callsign', 'Unknown')} has invalid position")
            return
        
        # Store aircraft data for redraw
        self.aircraft_data.append(aircraft_data)

        # Draw/create marker only for the new aircraft to avoid full redraw
        if self.show_aircraft_var.get():
            try:
                marker = self._create_or_update_aircraft_marker(aircraft_data)
                if marker:
                    callsign = aircraft_data.get('callsign', 'UNKNOWN')
                    self._aircraft_marker_index[callsign] = marker
                    # Store in map_markers list for cleanup
                    self.map_markers.append(marker)
                    self.aircraft_markers.append(marker)
                    

                    
                    if self.debug:
                        print(f"✓ Added aircraft {callsign}")
                else:
                    print(f"WARNING: Failed to create marker for {aircraft_data.get('callsign', 'Unknown')} at {aircraft_data.get('position')}")
            except Exception as e:
                print(f"ERROR adding aircraft {aircraft_data.get('callsign', 'Unknown')}: {e}")
    
    def draw_single_aircraft(self, aircraft_data):
        """Draw a single aircraft on the map with plane icon (wrapper)."""
        new_marker = self._create_or_update_aircraft_marker(aircraft_data)
        if new_marker:
            callsign = aircraft_data.get('callsign', 'UNKNOWN')
            self._aircraft_marker_index[callsign] = new_marker
            # Store in tracking lists
            if new_marker not in self.map_markers:
                self.map_markers.append(new_marker)
            if new_marker not in self.aircraft_markers:
                self.aircraft_markers.append(new_marker)
            print(f"✓ Drew aircraft {callsign}")
            return 1
        return 0

    def _create_or_update_aircraft_marker(self, aircraft_data):
        """Create a new marker for an aircraft using map widget markers."""
        try:
            callsign = aircraft_data.get('callsign', 'UNKNOWN')
            position = aircraft_data.get('position', '')
            altitude = aircraft_data.get('altitude', '')
            ac_type = aircraft_data.get('type', '')

            # Parse coordinates
            lat = lon = None
            if position and ',' in str(position):
                try:
                    lat_str, lon_str = str(position).split(',', 1)
                    lat = float(lat_str.strip())
                    lon = float(lon_str.strip())
                except (ValueError, IndexError):
                    print(f"DEBUG: Failed to parse position '{position}' for {callsign}")
                    return None
            elif hasattr(position, 'lat') and hasattr(position, 'lon'):
                try:
                    lat = float(position.lat)
                    lon = float(position.lon)
                except (ValueError, TypeError):
                    return None
            else:
                print(f"DEBUG: Invalid position format for {callsign}: {position}")
                return None

            # Validate coordinates
            if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                print(f"DEBUG: Invalid coordinates for {callsign}: lat={lat}, lon={lon}")
                return None

            # Check if marker already exists
            existing = self._aircraft_marker_index.get(callsign)
            if existing and hasattr(existing, 'set_position'):
                # Update position of existing marker
                try:
                    existing.set_position(lat, lon)
                    existing.aircraft_data = aircraft_data
                    print(f"DEBUG: Updated marker position for {callsign}")
                    return existing
                except Exception as e:
                    print(f"DEBUG: Could not update position: {e}")

            # Create new marker using map widget's set_marker
            try:
                # Create marker text showing callsign and altitude
                marker_text = f"{callsign}\n{altitude}"

                # Use blue for aircraft
                marker = self.map_widget.set_marker(
                    lat, lon,
                    text=marker_text,
                    marker_color_circle="blue",
                    marker_color_outside="lightblue",
                    font=("Arial", 8),
                    text_color="black"
                )

                if marker:
                    # Store reference and metadata
                    marker.callsign = callsign
                    marker.altitude = altitude
                    marker.ac_type = ac_type
                    marker.aircraft_data = aircraft_data
                    marker.position = (lat, lon)  # Store position for fit_to_data()

                    print(f"DEBUG: Created marker for {callsign} at ({lat:.4f}, {lon:.4f})")
                    return marker
                else:
                    print(f"DEBUG: set_marker returned None for {callsign}")
                    return None

            except Exception as e:
                print(f"DEBUG: Error creating marker for {callsign}: {e}")
                import traceback
                traceback.print_exc()
                return None

        except Exception as e:
            print(f"ERROR in _create_or_update_aircraft_marker: {e}")
            import traceback
            traceback.print_exc()
            return None

    def on_aircraft_click(self, event, marker):
        """Handle aircraft click for selection"""
        if hasattr(marker, 'callsign'):
            self.select_aircraft(marker.callsign, marker)
            print(f"✓ Selected aircraft: {marker.callsign}")

    def open_aircraft_editor_by_callsign(self, event, callsign):
        """Find aircraft by callsign and open editor"""
        marker = None
        obj = self._aircraft_marker_index.get(callsign)
        if obj:
            # obj may be dict if canvas-image approach
            try:
                aircraft_data = obj.get('aircraft_data')
                # reuse existing editor logic by creating a temporary marker-like object
                fake_marker = type('M', (), {})()
                fake_marker.aircraft_data = aircraft_data
                fake_marker.callsign = callsign
                self.open_aircraft_editor(event, fake_marker)
            except Exception:
                pass

    def _schedule_aircraft_reposition(self, delay=100):
        if getattr(self, '_reposition_after_id', None):
            try:
                self.parent.after_cancel(self._reposition_after_id)
            except Exception:
                pass
        try:
            self._reposition_after_id = self.parent.after(delay, self._update_all_aircraft_canvas_positions)
        except Exception:
            self._reposition_after_id = None

    def _on_map_button_press(self, event):
        """Start pan: record initial mouse decimal coord."""
        try:
            self._pan_start_xy = (event.x, event.y)
            self._pan_start_decimal = self.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
        except Exception:
            self._pan_start_xy = None
            self._pan_start_decimal = None

    def _on_map_drag(self, event):
        """Pan the map by dragging: compute decimal delta and move center accordingly."""
        if not hasattr(self, '_pan_start_decimal') or not self._pan_start_decimal:
            return
        try:
            cur_decimal = self.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
            if not cur_decimal:
                return
            lat0, lon0 = self._pan_start_decimal
            lat1, lon1 = cur_decimal

            # Compute delta from start to current (how the map moved under cursor)
            dlat = lat0 - lat1
            dlon = lon0 - lon1

            # Current center is canvas center position
            w = self.map_widget.canvas.winfo_width() // 2
            h = self.map_widget.canvas.winfo_height() // 2
            center = self.map_widget.convert_canvas_coords_to_decimal_coords(w, h)
            if not center:
                return
            center_lat, center_lon = center

            # New center is shifted by delta
            new_lat = center_lat + dlat
            new_lon = center_lon + dlon
            try:
                self.map_widget.set_position(new_lat, new_lon)
            except Exception:
                pass

            # schedule reposition of aircraft images
            self._schedule_aircraft_reposition(delay=10)
        except Exception:
            pass

    def _on_mouse_wheel(self, event):
        """Zoom map with mouse wheel. Positive delta -> zoom in."""
        try:
            # On Windows event.delta is multiple of 120
            delta = getattr(event, 'delta', None)
            if delta is None:
                # Button-4/5 on some linux platforms
                if str(event.num) == '4':
                    delta = 120
                elif str(event.num) == '5':
                    delta = -120
                else:
                    delta = 0

            if delta > 0:
                try:
                    self.map_widget.set_zoom(self.map_widget.zoom + 1)
                except Exception:
                    self.map_widget.set_zoom(self.map_widget.zoom)
            elif delta < 0:
                try:
                    self.map_widget.set_zoom(max(1, self.map_widget.zoom - 1))
                except Exception:
                    self.map_widget.set_zoom(self.map_widget.zoom)

            self._schedule_aircraft_reposition(delay=50)
        except Exception:
            pass

    def _update_all_aircraft_canvas_positions(self):
        """Reposition all canvas aircraft images to match current map transform."""
        self._reposition_after_id = None
        try:
            for cs, obj in list(self._aircraft_marker_index.items()):
                try:
                    if isinstance(obj, dict) and obj.get('canvas_id'):
                        lat = obj.get('lat')
                        lon = obj.get('lon')
                        if lat is None or lon is None:
                            continue
                        cx, cy = self.map_widget.convert_decimal_to_canvas_coords(lat, lon)
                        if cx is not None:
                            try:
                                self.map_widget.canvas.coords(obj['canvas_id'], cx, cy)
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

    def on_aircraft_start_drag(self, event, callsign):
        """Start dragging an aircraft polygon."""
        # Record dragging state
        try:
            self._dragging = {
                'callsign': callsign,
                'last_x': event.x,
                'last_y': event.y,
                'canvas_move_mode': True
            }
            # Ensure the aircraft is selected
            self.select_aircraft(callsign)
        except Exception:
            self._dragging = None

    def on_aircraft_drag(self, event, callsign):
        """Handle dragging motion - move polygon on canvas."""
        if not hasattr(self, '_dragging') or not self._dragging:
            return
        if self._dragging.get('callsign') != callsign:
            return

        dx = event.x - self._dragging['last_x']
        dy = event.y - self._dragging['last_y']
        try:
            # Move the canvas image if present
            obj = self._aircraft_marker_index.get(callsign)
            if obj and isinstance(obj, dict) and obj.get('canvas_id'):
                try:
                    self.map_widget.canvas.move(obj['canvas_id'], dx, dy)
                except Exception:
                    pass
            else:
                try:
                    self.map_widget.canvas.move(f"aircraft_{callsign}", dx, dy)
                except Exception:
                    pass
        except Exception:
            pass

        self._dragging['last_x'] = event.x
        self._dragging['last_y'] = event.y

    def on_aircraft_end_drag(self, event, callsign):
        """Finish dragging - convert canvas position to lat/lon and update marker/data."""
        if not hasattr(self, '_dragging') or not self._dragging:
            return
        if self._dragging.get('callsign') != callsign:
            self._dragging = None
            return

        # Get center of polygon (use event position)
        canvas_x = event.x
        canvas_y = event.y

        # Convert to map coordinates
        try:
            map_pos = self.map_widget.convert_canvas_coords_to_decimal_coords(canvas_x, canvas_y)
        except Exception:
            map_pos = None

        if map_pos:
            lat, lon = map_pos
            print(f"✓ Dragged aircraft {callsign} to {lat:.6f}, {lon:.6f}")

            # Update canvas marker data
            obj = self._aircraft_marker_index.get(callsign)
            if obj and isinstance(obj, dict):
                obj['lat'] = lat
                obj['lon'] = lon
                obj['aircraft_data']['position'] = f"{lat:.6f}, {lon:.6f}"
                # Reposition properly
                try:
                    cx, cy = self.map_widget.convert_decimal_to_canvas_coords(lat, lon)
                    if cx is not None:
                        self.map_widget.canvas.coords(obj['canvas_id'], cx, cy)
                except Exception:
                    pass

            # Notify parent if available
            try:
                home_page = self.parent.master.master.master
                if hasattr(home_page, 'on_aircraft_position_update'):
                    home_page.on_aircraft_position_update(callsign, f"{lat:.6f}, {lon:.6f}")
            except Exception:
                pass

        self._dragging = None

    def open_aircraft_editor(self, event, marker):
        """Open a simple dialog to edit aircraft details."""
        if not hasattr(marker, 'aircraft_data'):
            return
        data = marker.aircraft_data

        # Create editor window
        try:
            win = tk.Toplevel(self.parent)
            win.title(f"Edit Aircraft: {data.get('callsign', '')}")
            win.transient(self.parent)
            fields = ['callsign', 'position', 'heading', 'altitude', 'speed']
            entries = {}

            for i, field in enumerate(fields):
                tk.Label(win, text=field.capitalize()+":").grid(row=i, column=0, sticky='e', padx=4, pady=2)
                val = data.get(field, '')
                ent = tk.Entry(win, width=30)
                ent.grid(row=i, column=1, padx=4, pady=2)
                ent.insert(0, str(val))
                entries[field] = ent

            def save_and_close():
                # Update data
                for field, ent in entries.items():
                    data[field] = ent.get()

                # Update marker and redraw
                for i, aircraft in enumerate(self.aircraft_data):
                    if aircraft.get('callsign') == data.get('callsign') or aircraft.get('callsign') == marker.callsign:
                        self.aircraft_data[i] = data
                        break

                # Redraw aircraft
                self.draw_aircraft()

                # Notify parent if position changed
                pos = data.get('position', '')
                if ',' in pos:
                    try:
                        lat_str, lon_str = pos.split(',')
                        lat = float(lat_str.strip())
                        lon = float(lon_str.strip())
                        if hasattr(marker, 'callsign'):
                            try:
                                home_page = self.parent.master.master.master
                                if hasattr(home_page, 'on_aircraft_position_update'):
                                    home_page.on_aircraft_position_update(marker.callsign, pos)
                            except Exception:
                                pass
                    except Exception:
                        pass

                win.destroy()

            tk.Button(win, text="Save", command=save_and_close).grid(row=len(fields), column=0, columnspan=2, pady=6)
        except Exception as e:
            print(f"✗ Could not open editor: {e}")
    
    def select_aircraft(self, callsign, marker=None):
        """Select an aircraft on the map"""
        # Clear previous selection
        self.clear_aircraft_selection()

        # If a legacy marker object is provided, try to use it
        if marker and hasattr(marker, 'callsign'):
            try:
                marker.marker_color_circle = "red"
                marker.marker_color_outside = "darkred"
                marker.text_color = "white"
                if hasattr(marker, 'draw'):
                    try:
                        marker.draw()
                    except Exception:
                        pass
                if hasattr(marker, 'plane_polygon'):
                    try:
                        self.map_widget.canvas.itemconfig(marker.plane_polygon, fill="red", outline="yellow", width=2)
                    except Exception:
                        pass
            except Exception:
                pass

            self.selected_aircraft = callsign
            self.selected_aircraft_label.config(text=f"Selected: {callsign}", fg="red", font=("Arial", 9, "bold"))
            if hasattr(marker, 'position') and marker.position:
                try:
                    self.map_widget.set_position(marker.position[0], marker.position[1])
                    self.map_widget.set_zoom(12)
                except Exception:
                    pass
            return True

        # Otherwise look up canvas-based marker dict and update its image
        obj = self._aircraft_marker_index.get(callsign)
        if obj and isinstance(obj, dict):
            try:
                if PIL_AVAILABLE:
                    img = self._get_plane_photoimage(obj.get('heading', 0), size=32, color="#ff0000")
                    if img and obj.get('canvas_id'):
                        obj['_prev_image'] = obj.get('image')
                        obj['image'] = img
                        try:
                            self.map_widget.canvas.itemconfig(obj['canvas_id'], image=img)
                        except Exception:
                            pass
                        obj['_selected_image_ref'] = img
            except Exception:
                pass

            self.selected_aircraft = callsign
            self.selected_aircraft_label.config(text=f"Selected: {callsign}", fg="red", font=("Arial", 9, "bold"))
            # Center on aircraft if possible
            try:
                lat = obj.get('lat')
                lon = obj.get('lon')
                if lat is not None and lon is not None:
                    self.map_widget.set_position(lat, lon)
                    self.map_widget.set_zoom(12)
            except Exception:
                pass

            return True

        return False
    
    def clear_aircraft_selection(self):
        """Clear aircraft selection"""
        if not self.selected_aircraft:
            self.selected_aircraft_label.config(text="No aircraft selected", fg="blue", font=("Arial", 9))
            return

        # Restore legacy marker appearance if present
        for marker in self.aircraft_markers:
            try:
                if hasattr(marker, 'callsign') and marker.callsign == self.selected_aircraft:
                    marker.marker_color_circle = "blue"
                    marker.marker_color_outside = "white"
                    marker.text_color = "darkblue"
                    if hasattr(marker, 'draw'):
                        try:
                            marker.draw()
                        except Exception:
                            pass
                    if hasattr(marker, 'plane_polygon'):
                        try:
                            self.map_widget.canvas.itemconfig(marker.plane_polygon, fill="blue", outline="white", width=1.5)
                        except Exception:
                            pass
                    break
            except Exception:
                continue

        # Restore canvas-based aircraft image if present
        prev = self._aircraft_marker_index.get(self.selected_aircraft)
        if prev and isinstance(prev, dict):
            try:
                if PIL_AVAILABLE:
                    img = self._get_plane_photoimage(prev.get('heading', 0), size=28, color="#0000ff")
                else:
                    img = None
                if img and prev.get('canvas_id'):
                    try:
                        prev['image'] = img
                        self.map_widget.canvas.itemconfig(prev['canvas_id'], image=img)
                        prev['_image_ref'] = img
                    except Exception:
                        pass
            except Exception:
                pass

        self.selected_aircraft = None
        self.selected_aircraft_label.config(text="No aircraft selected", fg="blue", font=("Arial", 9))
    
    def add_airport_to_selection(self, airport_icao, airport_data):
        """Add airport to selection"""
        self.selected_airports[airport_icao] = airport_data
        self.update_selection_display()
    
    def remove_airport_from_selection(self, airport_icao):
        """Remove airport from selection"""
        if airport_icao in self.selected_airports:
            del self.selected_airports[airport_icao]
            self.update_selection_display()
    
    def add_runway_to_selection(self, runway_id, runway_data):
        """Add runway to selection"""
        print(f"DEBUG: Adding runway to selection - {runway_id}")
        # Store the complete runway data including coordinates
        if runway_id in self.runway_markers:
            marker_data = self.runway_markers[runway_id]
            if isinstance(marker_data, dict) and 'runway_data' in marker_data:
                # Use the runway data from runway_markers which has coordinates
                self.selected_runways[runway_id] = marker_data['runway_data']
                print(f"DEBUG: Stored runway data with coordinates for {runway_id}")
            else:
                # Fallback to provided runway_data
                self.selected_runways[runway_id] = runway_data
        else:
            self.selected_runways[runway_id] = runway_data
        print(f"DEBUG: selected_runways now: {list(self.selected_runways.keys())}")
        self.update_selection_display()
    
    def remove_runway_from_selection(self, runway_id):
        """Remove runway from selection"""
        if runway_id in self.selected_runways:
            del self.selected_runways[runway_id]
            self.update_selection_display()
    
    def update_selection_display(self):
        """Update the display label with current selections"""
        items = list(self.selected_airports.keys()) + list(self.selected_runways.keys())
        print(f"DEBUG: update_selection_display - items: {items}")
        if items:
            self.selection_label.config(text=", ".join(items[:5]) + ("..." if len(items) > 5 else ""))
        else:
            self.selection_label.config(text="None")
        
        # Redraw runway extensions to show selected ones in green
        print(f"DEBUG: Calling draw_runway_extensions, selected_runways: {list(self.selected_runways.keys())}")
        self.draw_runway_extensions()
    
    def clear_runway_airport_selection(self):
        """Clear all runway and airport selections"""
        self.selected_airports = {}
        self.selected_runways = {}
        self.update_selection_display()
        self.redraw_all()

    def redraw_all(self):
        """Redraw all map elements based on current visibility settings without reloading data"""
        if self.debug:
            print("DEBUG: redraw_all called - updating visibility")

        # Clear existing map elements
        self.clear_map()

        # Redraw SCT data if parsers available
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            try:
                data = self.sct_parser.get_data()
                self.draw_sct_data(data)
            except Exception as e:
                print(f"ERROR redrawing SCT data: {e}")

        # Redraw RWY data if parser available
        if self.rwy_parser and hasattr(self.rwy_parser, 'get_data'):
            try:
                data = self.rwy_parser.get_data()
                self.draw_rwy_data(data)
            except Exception as e:
                print(f"ERROR redrawing RWY data: {e}")

        # Redraw ESE data if parser available
        if self.ese_parser and hasattr(self.ese_parser, 'get_all_coordinates'):
            try:
                coordinates = self.ese_parser.get_all_coordinates()
                self.draw_ese_data(coordinates)
            except Exception as e:
                print(f"ERROR redrawing ESE data: {e}")

        # Draw runway extensions if enabled
        if self.show_runway_extensions_var.get():
            self.draw_runway_extensions()

        # Always redraw aircraft if enabled and we have data
        if self.show_aircraft_var.get() and self.aircraft_data:
            self.draw_aircraft()
            # Fit map to show aircraft if they were just drawn
            if self.aircraft_markers:
                self.fit_to_data()

        if self.debug:
            print("DEBUG: redraw_all completed")

        # Force canvas update to ensure all markers are visible
        try:
            self.map_widget.canvas.update()
            self.map_widget.canvas.update_idletasks()
        except:
            pass
    
    def on_airport_marker_click(self, marker, airport_icao, airport_data):
        """Handle airport marker click"""
        if airport_icao in self.selected_airports:
            # Deselect on second click
            self.remove_airport_from_selection(airport_icao)
            # If no airports selected, turn off extensions
            if not self.selected_airports:
                self.show_runway_extensions_var.set(False)
                self.redraw_all()
            # Restore original marker appearance
            try:
                marker.marker_color_circle = "red"
                marker.marker_color_outside = "pink"
                marker.text_color = "red"
                if hasattr(marker, 'draw'):
                    marker.draw()
            except:
                pass
        else:
            # Select
            self.add_airport_to_selection(airport_icao, airport_data)
            # Turn on runway extensions when airport is selected
            self.show_runway_extensions_var.set(True)

            # Select all runways for this airport
            self.selected_runways = {}
            for runway_id, runway_info in self.runway_markers.items():
                if isinstance(runway_info, dict) and 'runway_data' in runway_info:
                    self.selected_runways[runway_id] = runway_info['runway_data']
            print(f"DEBUG: Selected {len(self.selected_runways)} runways for airport {airport_icao}")

            self.redraw_all()
            # Highlight marker
            try:
                marker.marker_color_circle = "lime"
                marker.marker_color_outside = "lightgreen"
                marker.text_color = "darkgreen"
                if hasattr(marker, 'draw'):
                    marker.draw()
            except:
                pass
    
    def on_runway_path_click(self, runway_id, runway_data):
        """Handle runway path click"""
        print(f"DEBUG: on_runway_path_click called with runway_id={runway_id}")
        print(f"DEBUG: Current selected_runways BEFORE click: {list(self.selected_runways.keys())}")
        print(f"DEBUG: Check if '{runway_id}' in {list(self.selected_runways.keys())} = {runway_id in self.selected_runways}")
        if runway_id in self.selected_runways:
            # Deselect on second click
            print(f"DEBUG: Deselecting runway {runway_id}")
            self.remove_runway_from_selection(runway_id)
            # If no runways selected, turn off extensions
            if not self.selected_runways:
                self.show_runway_extensions_var.set(False)
                self.redraw_all()
        else:
            # Select
            print(f"DEBUG: Selecting runway {runway_id}")
            self.add_runway_to_selection(runway_id, runway_data)
            # Turn on runway extensions when a runway is selected
            self.show_runway_extensions_var.set(True)
            self.redraw_all()
    
    
    def on_map_double_click(self, event):
        """Handle map double-click to move selected aircraft"""
        if not self.selected_aircraft:
            print("✗ No aircraft selected to move")
            return
        
        # Convert canvas coordinates to map coordinates
        canvas_x = event.x
        canvas_y = event.y
        
        # Get map coordinates
        map_position = self.map_widget.convert_canvas_coords_to_decimal_coords(canvas_x, canvas_y)
        
        if map_position:
            lat, lon = map_position
            print(f"✓ Moving aircraft {self.selected_aircraft} to {lat:.4f}, {lon:.4f}")

            # Update canvas-based aircraft marker
            obj = self._aircraft_marker_index.get(self.selected_aircraft)
            if obj and isinstance(obj, dict):
                obj['lat'] = lat
                obj['lon'] = lon
                obj['aircraft_data']['position'] = f"{lat:.6f}, {lon:.6f}"
                try:
                    cx, cy = self.map_widget.convert_decimal_to_canvas_coords(lat, lon)
                    if cx is not None and obj.get('canvas_id'):
                        self.map_widget.canvas.coords(obj['canvas_id'], cx, cy)
                except Exception:
                    pass

                # Notify parent (home_page) about position update
                try:
                    home_page = self.parent.master.master.master
                    if hasattr(home_page, 'on_aircraft_position_update'):
                        home_page.on_aircraft_position_update(self.selected_aircraft, f"{lat:.6f}, {lon:.6f}")
                except Exception:
                    pass

                # Recenter on new position
                self.map_widget.set_position(lat, lon)
    
    def draw_aircraft(self):
        """Draw all stored aircraft"""
        if self.debug:
            print(f"DEBUG: Drawing {len(self.aircraft_data)} aircraft")
        # Clear existing aircraft markers
        for aircraft_marker in self.aircraft_markers:
            try:
                # Delete the plane polygon if it exists
                if hasattr(aircraft_marker, 'plane_polygon'):
                    try:
                        self.map_widget.canvas.delete(aircraft_marker.plane_polygon)
                    except:
                        pass
                # Delete the marker
                aircraft_marker.delete()
            except:
                pass
        self.aircraft_markers = []
        
        # Clear selection
        self.clear_aircraft_selection()
        
        # Draw all aircraft
        drawn_count = 0
        for aircraft in self.aircraft_data:
            drawn_count += self.draw_single_aircraft(aircraft)
        
        print(f"✓ Successfully drew {drawn_count} out of {len(self.aircraft_data)} aircraft")

        # Force canvas update to ensure markers are visible
        try:
            self.map_widget.canvas.update()
            self.map_widget.canvas.update_idletasks()
        except:
            pass
    
    def zoom_in(self):
        """Zoom in on map"""
        current_zoom = self.map_widget.zoom
        self.map_widget.set_zoom(current_zoom + 1)
        print(f"DEBUG: Zoomed in to {current_zoom + 1}")
    
    def zoom_out(self):
        """Zoom out on map"""
        current_zoom = self.map_widget.zoom
        new_zoom = max(1, current_zoom - 1)
        self.map_widget.set_zoom(new_zoom)
        print(f"DEBUG: Zoomed out to {new_zoom}")
    
    def fit_to_data(self):
        """Fit map view to show all data"""
        if self.debug:
            print("DEBUG: Fitting map to data...")
        
        # Collect all coordinates
        all_coords = []
        
        # Get coordinates from markers
        for marker in self.map_markers:
            if hasattr(marker, 'position') and marker.position:
                all_coords.append(marker.position)
        
        # Get coordinates from paths
        for path in self.map_paths:
            if hasattr(path, 'position_list') and path.position_list:
                all_coords.extend(path.position_list)
        
        # Get coordinates from aircraft
        for aircraft in self.aircraft_markers:
            if hasattr(aircraft, 'position') and aircraft.position:
                all_coords.append(aircraft.position)
        
        # Also check aircraft data for coordinates
        for aircraft in self.aircraft_data:
            position = aircraft.get('position', '')
            try:
                if ',' in position:
                    lat_str, lon_str = position.split(',')
                    lat = float(lat_str.strip())
                    lon = float(lon_str.strip())
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        all_coords.append((lat, lon))
            except:
                pass
        
        print(f"DEBUG: fit_to_data found {len(all_coords)} coordinates")
        print(f"  - map_markers: {len(self.map_markers)}")
        print(f"  - map_paths: {len(self.map_paths)}")
        print(f"  - aircraft_markers: {len(self.aircraft_markers)}")
        print(f"  - aircraft_data: {len(self.aircraft_data)}")
        
        if all_coords:
            # Filter out None values and invalid coordinates
            valid_coords = []
            for coord in all_coords:
                if coord and len(coord) >= 2:
                    try:
                        lat, lon = float(coord[0]), float(coord[1])
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            valid_coords.append((lat, lon))
                    except:
                        pass
            
            print(f"DEBUG: fit_to_data found {len(valid_coords)} valid coordinates")
            
            if valid_coords:
                # Calculate bounds
                lats = [coord[0] for coord in valid_coords]
                lons = [coord[1] for coord in valid_coords]
                
                center_lat = (min(lats) + max(lats)) / 2
                center_lon = (min(lons) + max(lons)) / 2
                
                # Calculate zoom level based on spread
                lat_spread = max(lats) - min(lats)
                lon_spread = max(lons) - min(lons)
                max_spread = max(lat_spread, lon_spread)
                
                # Set position
                self.map_widget.set_position(center_lat, center_lon)

                # Adjust zoom based on spread
                if max_spread > 40:
                    zoom = 3
                elif max_spread > 20:
                    zoom = 4
                elif max_spread > 10:
                    zoom = 5
                elif max_spread > 5:
                    zoom = 6
                elif max_spread > 2:
                    zoom = 7
                elif max_spread > 1:
                    zoom = 8
                elif max_spread > 0.5:
                    zoom = 9
                elif max_spread > 0.2:
                    zoom = 10
                elif max_spread > 0.1:
                    zoom = 11
                elif max_spread > 0.05:
                    zoom = 12
                else:
                    zoom = 13

                self.map_widget.set_zoom(zoom)
                # Force update to reposition markers
                self.map_widget.canvas.update()
                self.map_widget.canvas.update_idletasks()
                print(f"✓ Set map to center: {center_lat:.4f}, {center_lon:.4f}, zoom: {zoom}, spread: {max_spread:.2f}")
            else:
                print("✗ No valid coordinates to fit - showing default view")
                self.map_widget.set_position(0.0, 0.0)
                self.map_widget.set_zoom(3)
        else:
            print("✗ No coordinates found to fit - showing default view")
            self.map_widget.set_position(0.0, 0.0)
            self.map_widget.set_zoom(3)
    




    def get_entry_fixes(self):
        """Get entry fixes for selected airport"""
        entry_fixes = []
        
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            data = self.sct_parser.get_data()
            if 'fixes' in data:
                for fix in data['fixes'][:20]:  # First 20 fixes
                    if 'latitude' in fix and 'longitude' in fix and 'name' in fix:
                        # Calculate distance from selected airport if available
                        distance = 50  # Default
                        if self.selected_airport and 'airports' in data:
                            for airport in data['airports']:
                                if airport.get('icao') == self.selected_airport:
                                    if 'latitude' in airport and 'longitude' in airport:
                                        # Simple distance calculation
                                        try:
                                            lat_diff = abs(float(fix['latitude']) - float(airport['latitude']))
                                            lon_diff = abs(float(fix['longitude']) - float(airport['longitude']))
                                            distance = int((lat_diff + lon_diff) * 60)  # Approximate NM
                                        except:
                                            pass
                                        break
                        
                        entry_fixes.append({
                            'name': fix['name'],
                            'lat': float(fix['latitude']),
                            'lon': float(fix['longitude']),
                            'distance_nm': distance
                        })
        
        if self.debug:
            print(f"DEBUG: Found {len(entry_fixes)} entry fixes")
        return entry_fixes
    
    def get_selected_airport(self):
        """Get currently selected airport"""
        return self.selected_airport
    
    def get_selected_aircraft(self):
        """Get currently selected aircraft"""
        return self.selected_aircraft

    def fetch_runway_data_for_airport(self, icao):
        """Try to obtain runway/centerline data for the given ICAO.

        Strategy:
        - If a RWY parser is available, use its parsed runways (assumed to be for the loaded airport file).
        - Otherwise attempt an online fetch from a known airport dataset (best-effort).
        """
        if not icao:
            return False

        drawn = 0

        # 1) Use local RWY parser if present
        try:
            if self.rwy_parser and hasattr(self.rwy_parser, 'get_data'):
                data = self.rwy_parser.get_data()
                runways = data.get('runways', []) if isinstance(data, dict) else []
                if runways:
                    # Draw runways from local parser
                    for rwy in runways:
                        coords = rwy.get('coordinates') if isinstance(rwy, dict) else None
                        if coords and len(coords) >= 2 and self.show_runways_var.get():
                            try:
                                path = self.map_widget.set_path(coords, color="orange", width=3)
                                if path:
                                    self.map_paths.append(path)
                                    drawn += 1
                            except Exception:
                                pass

                    if drawn:
                        print(f"DEBUG: Drew {drawn} runways from local RWY parser for {icao}")
                        return True
        except Exception:
            pass

        # 2) Use SCT parser runways (if available) as a fallback
        try:
            if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
                sct_data = self.sct_parser.get_data()
                sct_runways = sct_data.get('runways', []) if isinstance(sct_data, dict) else []
                if sct_runways:
                    for runway in sct_runways:
                        coords = []
                        try:
                            for coord in runway.get('coordinates', []):
                                if hasattr(coord, 'lat') and hasattr(coord, 'lon'):
                                    lat = float(coord.lat)
                                    lon = float(coord.lon)
                                elif isinstance(coord, dict) and 'lat' in coord and 'lon' in coord:
                                    lat = float(coord['lat'])
                                    lon = float(coord['lon'])
                                elif isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                    lat = float(coord[0])
                                    lon = float(coord[1])
                                else:
                                    continue

                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    coords.append((lat, lon))
                        except Exception:
                            continue

                        if len(coords) >= 2 and self.show_runways_var.get():
                            try:
                                path = self.map_widget.set_path(coords, color="orange", width=3)
                                if path:
                                    self.map_paths.append(path)
                                    drawn += 1
                            except Exception:
                                pass

                    if drawn:
                        print(f"DEBUG: Drew {drawn} runways for {icao} from SCT parser data")
                        return True
        except Exception:
            pass

        # 3) Try an online dataset (best-effort). Use mwgg/Airports JSON as a fallback.
        try:
            import requests
            url = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                try:
                    airports = resp.json()
                    key = icao.upper()
                    if key in airports:
                        ap = airports[key]
                        # Try to locate basic airport lat/lon and mark it
                        lat = ap.get('lat') or ap.get('latitude') or ap.get('latdeg')
                        lon = ap.get('lon') or ap.get('longitude') or ap.get('londeg')
                        if lat and lon and self.show_runways_var.get():
                            try:
                                m = self.map_widget.set_marker(float(lat), float(lon), text=icao, marker_color_circle="red")
                                if m:
                                    self.map_markers.append(m)
                                    drawn += 1
                            except Exception:
                                pass

                        # Some datasets may include runway arrays; attempt to draw if present
                        runways = None
                        if isinstance(ap, dict):
                            runways = ap.get('runways') or ap.get('runway')

                        if runways and isinstance(runways, list):
                            for r in runways:
                                # Attempt common structures
                                coords = None
                                if isinstance(r, dict) and 'coordinates' in r:
                                    coords = r.get('coordinates')
                                elif isinstance(r, (list, tuple)) and len(r) >= 2 and isinstance(r[0], (list, tuple)):
                                    coords = r

                                if coords and len(coords) >= 2 and self.show_runways_var.get():
                                    try:
                                        # Normalize coords to floats
                                        norm = []
                                        for c in coords:
                                            if isinstance(c, (list, tuple)) and len(c) >= 2:
                                                latc = float(c[0]); lonc = float(c[1])
                                                norm.append((latc, lonc))
                                        if len(norm) >= 2:
                                            path = self.map_widget.set_path(norm, color="orange", width=3)
                                            if path:
                                                self.map_paths.append(path)
                                                drawn += 1
                                    except Exception:
                                        pass

                        if drawn:
                            print(f"DEBUG: Drew {drawn} runway/airport items for {icao} from online dataset")
                            return True
                except Exception:
                    pass
        except Exception:
            # requests not available or network error
            pass

        # If nothing found, leave as-is
        print(f"DEBUG: No external runway data found for {icao}")
        return False

    # Web map functionality
    def start_web_map_server(self):
        """Start a Flask web server to serve the map on localhost"""
        if not WEB_MAP_AVAILABLE:
            print("ERROR: Web map dependencies not available (Flask, Folium)")
            return False

        try:
            # Create Flask app
            self.web_app = Flask(__name__)

            @self.web_app.route('/')
            def index():
                return self.generate_web_map_html()

            # Start server in background thread
            self.web_thread = threading.Thread(target=lambda: self.web_app.run(host='localhost', port=5000, debug=False, use_reloader=False))
            self.web_thread.daemon = True
            self.web_thread.start()

            # Open browser
            webbrowser.open('http://localhost:5000')

            print("✓ Web map server started on http://localhost:5000")
            return True
        except Exception as e:
            print(f"ERROR: Failed to start web map server: {e}")
            return False

    def generate_web_map_html(self):
        """Generate HTML for web map using Folium"""
        try:
            # Create base map centered on selected airport or default
            center_lat, center_lon = 0.0, 0.0
            zoom_start = 3

            if self.selected_airport and self.sct_parser:
                data = self.sct_parser.get_data()
                if 'airports' in data:
                    for airport in data['airports']:
                        if airport.get('icao') == self.selected_airport:
                            try:
                                center_lat = float(airport.get('latitude', 0))
                                center_lon = float(airport.get('longitude', 0))
                                zoom_start = 10
                                break
                            except:
                                pass

            # Create Folium map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)

            # Add airports
            if self.sct_parser:
                data = self.sct_parser.get_data()
                if 'airports' in data and data['airports']:
                    for airport in data['airports'][:50]:  # Limit for performance
                        try:
                            lat = float(airport.get('latitude', 0))
                            lon = float(airport.get('longitude', 0))
                            icao = airport.get('icao', 'N/A')

                            if -90 <= lat <= 90 and -180 <= lon <= 180 and lat != 0 and lon != 0:
                                folium.Marker(
                                    [lat, lon],
                                    popup=f"Airport: {icao}",
                                    icon=folium.Icon(color='red', icon='plane')
                                ).add_to(m)
                        except:
                            pass

            # Add aircraft
            if self.aircraft_data:
                for aircraft in self.aircraft_data:
                    try:
                        position = aircraft.get('position', '')
                        if ',' in position:
                            lat_str, lon_str = position.split(',')
                            lat = float(lat_str.strip())
                            lon = float(lon_str.strip())

                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                callsign = aircraft.get('callsign', 'UNKNOWN')
                                altitude = aircraft.get('altitude', 'Unknown')

                                folium.Marker(
                                    [lat, lon],
                                    popup=f"Aircraft: {callsign}<br>Altitude: {altitude}",
                                    icon=folium.Icon(color='blue', icon='plane', prefix='fa')
                                ).add_to(m)
                    except:
                        pass

            # Add fixes
            if self.sct_parser:
                data = self.sct_parser.get_data()
                if 'fixes' in data and data['fixes']:
                    for fix in data['fixes'][:100]:  # Limit for performance
                        try:
                            lat = float(fix.get('latitude', 0))
                            lon = float(fix.get('longitude', 0))
                            name = fix.get('name', 'UNK')

                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                folium.CircleMarker(
                                    [lat, lon],
                                    radius=3,
                                    popup=f"Fix: {name}",
                                    color='green',
                                    fill=True
                                ).add_to(m)
                        except:
                            pass

            return m._repr_html_()

        except Exception as e:
            return f"<html><body><h1>Error generating map: {str(e)}</h1></body></html>"

    def toggle_web_map(self):
        """Toggle between app map and embedded web map"""
        if not TKINTERWEB_AVAILABLE:
            print("ERROR: tkinterweb not available for embedded web map")
            return

        try:
            # Check if web view is currently visible
            if hasattr(self, 'web_view') and self.web_view and self.web_view.winfo_ismapped():
                # Web view is visible, switch back to app map
                self.web_view.pack_forget()
                self.map_widget.pack(fill="both", expand=True)
                print("✓ Switched back to app map")
            else:
                # Show web view
                if hasattr(self, 'web_view') and self.web_view:
                    # Generate HTML and load into web view
                    html_content = self.generate_web_map_html()
                    self.web_view.load_html(html_content)

                    # Hide app map and show web view
                    self.map_widget.pack_forget()
                    self.web_view.pack(fill="both", expand=True)
                    print("✓ Switched to embedded web map")
                else:
                    print("ERROR: Web view not initialized")
        except Exception as e:
            print(f"ERROR: Failed to toggle web map: {e}")
