# sweatbox_map.py
import tkinter as tk
from tkinter import ttk
import tkintermapview
import re
import math

class SweatboxMapViewer:
    def __init__(self, parent, ese_parser=None, sct_parser=None, rwy_parser=None):
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
        
        # Aircraft selection
        self.selected_aircraft = None
        self.aircraft_click_bind_id = None
        
        # Initialize map
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the map interface"""
        # Create a main frame for the map
        main_frame = tk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True)
        
        # Create control frame at the top
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Airport selection
        tk.Label(control_frame, text="Select Airport:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        self.airport_var = tk.StringVar()
        self.airport_combo = ttk.Combobox(control_frame, textvariable=self.airport_var, width=20, state="readonly")
        self.airport_combo.pack(side=tk.LEFT, padx=5)
        self.airport_combo.bind("<<ComboboxSelected>>", self.on_airport_selected)
        
        # Zoom controls
        tk.Button(control_frame, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=5)
        
        # Fit to data button
        tk.Button(control_frame, text="Fit to Data", command=self.fit_to_data).pack(side=tk.LEFT, padx=5)
        
        # Reload data button
        tk.Button(control_frame, text="Reload Data", command=self.force_reload_data).pack(side=tk.LEFT, padx=5)
        
        # Aircraft control label
        tk.Label(control_frame, text="| Aircraft:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(20, 5))
        
        # Aircraft selection info
        self.selected_aircraft_label = tk.Label(control_frame, text="No aircraft selected", bg='#f0f0f0', fg='blue')
        self.selected_aircraft_label.pack(side=tk.LEFT, padx=5)
        
        # Clear selection button
        tk.Button(control_frame, text="Clear Selection", command=self.clear_aircraft_selection, 
                 bg='#ff9999', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Show/hide controls
        tk.Label(control_frame, text="Show:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(20, 5))
        self.show_aircraft_var = tk.BooleanVar(value=True)
        self.show_fixes_var = tk.BooleanVar(value=True)
        self.show_runways_var = tk.BooleanVar(value=True)
        self.show_boundaries_var = tk.BooleanVar(value=True)
        self.show_airports_var = tk.BooleanVar(value=True)
        self.show_runway_extensions_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(control_frame, text="Airports", variable=self.show_airports_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(control_frame, text="Fixes", variable=self.show_fixes_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(control_frame, text="Runways", variable=self.show_runways_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(control_frame, text="RWY Extensions", variable=self.show_runway_extensions_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(control_frame, text="Boundaries", variable=self.show_boundaries_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(control_frame, text="Aircraft", variable=self.show_aircraft_var,
                      command=self.redraw_all, bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        
        # Create map widget BELOW controls
        self.map_widget = tkintermapview.TkinterMapView(main_frame, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        
        # Set default position (world view)
        self.map_widget.set_position(0.0, 0.0)
        self.map_widget.set_zoom(3)
        
        # Set tile server to OpenStreetMap
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        
        # Bind double-click for aircraft movement
        self.map_widget.canvas.bind("<Double-Button-1>", self.on_map_double_click)
    
    def update_airports(self, airports):
        """Update the airport dropdown with extracted airports"""
        self.loaded_airports = airports
        self.airport_combo['values'] = airports
        if airports:
            self.airport_combo.set(airports[0])
            self.selected_airport = airports[0]
    
    def load_data(self):
        """Load data from parsers and display on map"""
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
            print("DEBUG: Fitted map to data")
        else:
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
                        marker = self.map_widget.set_marker(
                            lat, lon,
                            text=icao,
                            marker_color_circle="red",
                            marker_color_outside="pink",
                            text_color="red",
                            font=("Arial", 10, "bold")
                        )
                        if marker:
                            self.map_markers.append(marker)
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
            print(f"DEBUG: Drawing {len(data['runways'])} runways from SCT")
            for runway in data['runways']:
                if 'coordinates' in runway and runway['coordinates']:
                    coords = []
                    try:
                        for coord in runway['coordinates']:
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
                        
                        if len(coords) >= 2:
                            path = self.map_widget.set_path(coords, color="gray", width=3)
                            if path:
                                self.map_paths.append(path)
                                items_drawn += 1
                    except (ValueError, TypeError) as e:
                        print(f"  ✗ Error drawing runway: {e}")
        
        # Draw ARTCC boundaries (AIRSPACE) - FIXED VERSION
        if self.show_boundaries_var.get():
            # High boundaries
            if 'ARTCC_HIGH' in data and data['ARTCC_HIGH']:
                print(f"DEBUG: Drawing {len(data['ARTCC_HIGH'])} ARTCC HIGH boundaries")
                items_drawn += self.draw_boundaries_fixed(data['ARTCC_HIGH'], "red", width=2, name="ARTCC_HIGH")
            
            # Low boundaries
            if 'ARTCC_LOW' in data and data['ARTCC_LOW']:
                print(f"DEBUG: Drawing {len(data['ARTCC_LOW'])} ARTCC LOW boundaries")
                items_drawn += self.draw_boundaries_fixed(data['ARTCC_LOW'], "blue", width=1, name="ARTCC_LOW")
            
            # Also check for regular ARTCC
            if 'ARTCC' in data and data['ARTCC']:
                print(f"DEBUG: Drawing {len(data['ARTCC'])} ARTCC boundaries")
                items_drawn += self.draw_boundaries_fixed(data['ARTCC'], "orange", width=1, name="ARTCC")
        
        return items_drawn
    
    def draw_boundaries_fixed(self, boundaries, color, width=1, name="BOUNDARY"):
        """Draw boundary lines on map - FIXED VERSION - returns count of items drawn"""
        items_drawn = 0
        if not boundaries:
            return items_drawn
            
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
        if not coordinates:
            return items_drawn
            
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
    
    def draw_runway_extensions(self):
        """Draw 20NM extensions on both ends of runways - returns count of items drawn"""
        items_drawn = 0
        
        # Clear existing extensions
        for extension in self.runway_extensions:
            try:
                extension.delete()
            except:
                pass
        self.runway_extensions = []
        
        # Get runways from SCT parser
        if self.sct_parser and hasattr(self.sct_parser, 'get_data'):
            try:
                data = self.sct_parser.get_data()
                if 'runways' in data and data['runways']:
                    print(f"DEBUG: Drawing extensions for {len(data['runways'])} runways")
                    
                    for runway in data['runways'][:20]:  # Limit to first 20 for performance
                        if 'coordinates' in runway and runway['coordinates']:
                            try:
                                # Get runway coordinates
                                coords = []
                                for coord in runway['coordinates']:
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
                                
                                if len(coords) >= 2:
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
                                    
                                    # Draw extension lines
                                    if ext_start and ext_end:
                                        # Draw extension from start
                                        path1 = self.map_widget.set_path(
                                            [coords[0], ext_start],
                                            color="darkgray",
                                            width=1,
                                            dash=(5, 2)  # Dashed line
                                        )
                                        if path1:
                                            self.runway_extensions.append(path1)
                                            items_drawn += 1
                                        
                                        # Draw extension from end
                                        path2 = self.map_widget.set_path(
                                            [coords[-1], ext_end],
                                            color="darkgray",
                                            width=1,
                                            dash=(5, 2)  # Dashed line
                                        )
                                        if path2:
                                            self.runway_extensions.append(path2)
                                            items_drawn += 1
                                        
                                        # Mark extension points
                                        marker1 = self.map_widget.set_marker(
                                            ext_start[0], ext_start[1],
                                            text="20NM",
                                            marker_color_circle="lightgray",
                                            font=("Arial", 6)
                                        )
                                        if marker1:
                                            self.map_markers.append(marker1)
                                        
                                        marker2 = self.map_widget.set_marker(
                                            ext_end[0], ext_end[1],
                                            text="20NM",
                                            marker_color_circle="lightgray",
                                            font=("Arial", 6)
                                        )
                                        if marker2:
                                            self.map_markers.append(marker2)
                                        
                            except Exception as e:
                                print(f"  ✗ Error drawing runway extension: {e}")
            except Exception as e:
                print(f"ERROR drawing runway extensions: {e}")
        
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
    
    def force_reload_data(self):
        """Force reload all data - useful for debugging"""
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
        
        # Clear aircraft markers (but keep aircraft data)
        for aircraft_marker in self.aircraft_markers:
            try:
                aircraft_marker.delete()
            except:
                pass
        self.aircraft_markers = []
        
        # Clear runway extensions
        for extension in self.runway_extensions:
            try:
                extension.delete()
            except:
                pass
        self.runway_extensions = []
    
    def clear_aircraft(self):
        """Clear only aircraft markers and data"""
        for aircraft_marker in self.aircraft_markers:
            try:
                aircraft_marker.delete()
            except:
                pass
        self.aircraft_markers = []
        self.aircraft_data = []
        self.clear_aircraft_selection()
    
    def add_aircraft(self, aircraft_data):
        """Add aircraft to map and store data"""
        # Store aircraft data for redraw
        self.aircraft_data.append(aircraft_data)
        
        # Draw if aircraft visibility is on
        if self.show_aircraft_var.get():
            items_drawn = self.draw_single_aircraft(aircraft_data)
            if items_drawn > 0:
                print(f"✓ Added aircraft {aircraft_data.get('callsign', 'Unknown')}")
    
    def draw_single_aircraft(self, aircraft_data):
        """Draw a single aircraft on map - returns 1 if drawn, 0 if not"""
        position = aircraft_data.get('position', '')
        callsign = aircraft_data.get('callsign', '')
        heading = aircraft_data.get('heading', '000')
        
        # Parse heading
        try:
            heading_deg = float(heading) % 360
        except:
            heading_deg = 0
        
        # Parse position string
        try:
            if ',' in position:
                lat_str, lon_str = position.split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
            else:
                # Try to extract from other formats
                coords = re.findall(r'[-+]?\d*\.\d+|\d+', position)
                if len(coords) >= 2:
                    lat = float(coords[0])
                    lon = float(coords[1])
                else:
                    # Try to get from SCT airports if available
                    if self.sct_parser and callsign[:4] in self.loaded_airports:
                        data = self.sct_parser.get_data()
                        if 'airports' in data:
                            for airport in data['airports']:
                                if airport.get('icao') == callsign[:4]:
                                    lat = float(airport['latitude'])
                                    lon = float(airport['longitude'])
                                    break
                            else:
                                lat, lon = 0, 0  # Default
                    else:
                        lat, lon = 0, 0  # Default
            
            # Validate coordinates
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                # Create aircraft marker
                marker = self.map_widget.set_marker(
                    lat, lon,
                    text=callsign,
                    marker_color_circle="cyan",
                    marker_color_outside="darkblue",
                    text_color="black",
                    font=("Arial", 9, "bold")
                )
                if marker:
                    # Store aircraft data with the marker
                    marker.aircraft_data = aircraft_data
                    marker.callsign = callsign
                    
                    # Bind click event for selection
                    marker.bind("<Button-1>", lambda e, m=marker: self.on_aircraft_click(e, m))
                    
                    self.aircraft_markers.append(marker)
                    return 1
                else:
                    print(f"  ✗ Failed to create marker for {callsign}")
            else:
                print(f"  ✗ Invalid coordinates for aircraft {callsign}: {lat}, {lon}")
            
        except (ValueError, AttributeError, TypeError) as e:
            print(f"  ✗ Error adding aircraft {callsign}: {e}")
        
        return 0
    
    def on_aircraft_click(self, event, marker):
        """Handle aircraft click for selection"""
        if hasattr(marker, 'callsign'):
            self.select_aircraft(marker.callsign, marker)
            print(f"✓ Selected aircraft: {marker.callsign}")
    
    def select_aircraft(self, callsign, marker=None):
        """Select an aircraft on the map"""
        # Clear previous selection
        self.clear_aircraft_selection()
        
        # Find the marker if not provided
        if not marker:
            for m in self.aircraft_markers:
                if hasattr(m, 'callsign') and m.callsign == callsign:
                    marker = m
                    break
        
        if marker:
            # Highlight the selected aircraft
            marker.marker_color_circle = "red"
            marker.marker_color_outside = "darkred"
            marker.text_color = "white"
            
            # Update the marker appearance
            try:
                marker.draw()
            except:
                pass
            
            self.selected_aircraft = callsign
            self.selected_aircraft_label.config(
                text=f"Selected: {callsign}",
                fg="red",
                font=("Arial", 9, "bold")
            )
            
            # Center map on selected aircraft
            if hasattr(marker, 'position'):
                self.map_widget.set_position(marker.position[0], marker.position[1])
                self.map_widget.set_zoom(12)
            
            return True
        
        return False
    
    def clear_aircraft_selection(self):
        """Clear aircraft selection"""
        if self.selected_aircraft:
            # Find and restore the previously selected aircraft
            for marker in self.aircraft_markers:
                if hasattr(marker, 'callsign') and marker.callsign == self.selected_aircraft:
                    # Restore original colors
                    marker.marker_color_circle = "cyan"
                    marker.marker_color_outside = "darkblue"
                    marker.text_color = "black"
                    
                    # Update the marker appearance
                    try:
                        marker.draw()
                    except:
                        pass
                    break
        
        self.selected_aircraft = None
        self.selected_aircraft_label.config(
            text="No aircraft selected",
            fg="blue",
            font=("Arial", 9)
        )
    
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
            
            # Find and update the aircraft marker
            for marker in self.aircraft_markers:
                if hasattr(marker, 'callsign') and marker.callsign == self.selected_aircraft:
                    # Update marker position
                    marker.set_position(lat, lon)
                    
                    # Update aircraft data
                    for i, aircraft in enumerate(self.aircraft_data):
                        if aircraft.get('callsign') == self.selected_aircraft:
                            self.aircraft_data[i]['position'] = f"{lat:.6f}, {lon:.6f}"
                            break
                    
                    # Notify parent (home_page) about position update
                    if hasattr(self.parent, 'on_aircraft_position_update'):
                        try:
                            # Get the parent of parent (HomePage)
                            home_page = self.parent.master.master.master
                            if hasattr(home_page, 'on_aircraft_position_update'):
                                home_page.on_aircraft_position_update(self.selected_aircraft, f"{lat:.6f}, {lon:.6f}")
                        except:
                            pass
                    
                    # Recenter on new position
                    self.map_widget.set_position(lat, lon)
                    break
    
    def draw_aircraft(self):
        """Draw all stored aircraft"""
        print(f"DEBUG: Drawing {len(self.aircraft_data)} aircraft")
        # Clear existing aircraft markers
        for aircraft_marker in self.aircraft_markers:
            try:
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
        
        print(f"DEBUG: Found {len(all_coords)} coordinates to fit")
        
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
                print(f"✓ Set map to center: {center_lat:.4f}, {center_lon:.4f}, zoom: {zoom}, spread: {max_spread:.2f}")
            else:
                print("✗ No valid coordinates to fit - showing default view")
                self.map_widget.set_position(0.0, 0.0)
                self.map_widget.set_zoom(3)
        else:
            print("✗ No coordinates found to fit - showing default view")
            self.map_widget.set_position(0.0, 0.0)
            self.map_widget.set_zoom(3)
    
    def redraw_all(self):
        """Redraw all data with current visibility settings"""
        print("DEBUG: Redrawing all data with current visibility settings")
        # Store current aircraft data and selection
        current_aircraft = self.aircraft_data.copy()
        selected = self.selected_aircraft
        
        # Clear and reload all data
        self.load_data()
        
        # Restore aircraft data
        self.aircraft_data = current_aircraft
        if self.show_aircraft_var.get():
            self.draw_aircraft()
            
            # Restore selection if it existed
            if selected:
                self.select_aircraft(selected)
    
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
        
        print(f"DEBUG: Found {len(entry_fixes)} entry fixes")
        return entry_fixes
    
    def get_selected_airport(self):
        """Get currently selected airport"""
        return self.selected_airport
    
    def get_selected_aircraft(self):
        """Get currently selected aircraft"""
        return self.selected_aircraft