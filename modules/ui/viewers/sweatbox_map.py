import tkinter as tk
import math
from tkinter import ttk

class SweatboxMapViewer:
    def __init__(self, parent, ese_parser=None, sct_parser=None, rwy_parser=None):
        self.parent = parent
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        self.rwy_parser = rwy_parser
        
        # Store data
        self.artcc_high_boundaries = []
        self.artcc_low_boundaries = []
        self.airport_points = []
        self.fix_points = []
        self.vor_points = []
        self.ndb_points = []
        self.runway_extensions = []
        self.ils_points = []
        self.aircraft_points = []
        self.selected_airport = None
        self.entry_fixes = []
        self.runway_centerlines = []
        
        # Drawn items
        self.drawn_paths = []
        self.drawn_markers = []
        self.aircraft_markers = []
        self.aircraft_tags = []
        self.extended_lines = []
        self.entry_fix_markers = []
        self.runway_line_markers = []
        self.airport_markers = []
        
        # Map widget
        self.map_widget = None
        
        # Settings
        self.show_extended_centerlines = True
        self.show_airspace = True
        self.show_aircraft_tags = True
        self.show_entry_fixes = True
        self.show_runway_centerlines = True
        
        # Drag state
        self.dragging_aircraft = None
        self.drag_start_pos = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='white', height=50)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)
        
        title_label = tk.Label(
            control_frame,
            text="Sweatbox Map Viewer",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(side='left', padx=10, pady=5)
        
        # Airport selector
        airport_frame = tk.Frame(control_frame, bg='white')
        airport_frame.pack(side='left', padx=20)
        
        tk.Label(airport_frame, text="Controlled Airport:", 
                bg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=(0, 5))
        
        self.airport_var = tk.StringVar()
        self.airport_combo = ttk.Combobox(airport_frame, textvariable=self.airport_var, 
                                         width=12, state='readonly', font=('Arial', 9))
        self.airport_combo.pack(side='left')
        self.airport_combo.bind('<<ComboboxSelected>>', self.on_airport_selected)
        
        refresh_btn = tk.Button(airport_frame, text="↻", 
                               command=self.refresh_airport_list,
                               bg='#3498db', fg='white', 
                               font=('Arial', 9, 'bold'),
                               width=2)
        refresh_btn.pack(side='left', padx=(5, 0))
        
        # Display controls
        controls_frame = tk.Frame(control_frame, bg='white')
        controls_frame.pack(side='right', padx=10)
        
        # Checkbuttons
        self.show_ext_var = tk.BooleanVar(value=True)
        self.show_airspace_var = tk.BooleanVar(value=True)
        self.show_tags_var = tk.BooleanVar(value=True)
        self.show_entry_var = tk.BooleanVar(value=True)
        self.show_centerlines_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(controls_frame, text="Runways", variable=self.show_centerlines_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=3)
        tk.Checkbutton(controls_frame, text="Centerlines", variable=self.show_ext_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=3)
        tk.Checkbutton(controls_frame, text="Airspace", variable=self.show_airspace_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=3)
        tk.Checkbutton(controls_frame, text="Entry Fixes", variable=self.show_entry_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=3)
        tk.Checkbutton(controls_frame, text="Aircraft Tags", variable=self.show_tags_var,
                      bg='white', font=('Arial', 9), command=self.toggle_tags).pack(side='left', padx=3)
        
        # Create map widget with error handling
        self.map_frame = tk.Frame(main_frame, bg='white')
        self.map_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        try:
            from tkintermapview import TkinterMapView
            self.map_widget = TkinterMapView(self.map_frame, width=800, height=600, corner_radius=0)
            self.map_widget.pack(fill='both', expand=True)
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)
            
            # Bind mouse events for dragging
            self.map_widget.canvas.bind('<ButtonPress-1>', self.on_map_click)
            self.map_widget.canvas.bind('<B1-Motion>', self.on_map_drag)
            self.map_widget.canvas.bind('<ButtonRelease-1>', self.on_map_release)
            
            # Set default position (South Africa)
            self.map_widget.set_position(-26.145, 28.234)
            self.map_widget.set_zoom(10)
            
        except ImportError as e:
            error_label = tk.Label(self.map_frame, 
                                  text="Map unavailable: tkintermapview not installed\nPlease run: pip install tkintermapview",
                                  font=('Arial', 10),
                                  bg='white',
                                  fg='red')
            error_label.pack(fill='both', expand=True, padx=20, pady=20)
            self.map_widget = None
            print("Warning: tkintermapview not installed. Map features disabled.")
        
        except Exception as e:
            error_label = tk.Label(self.map_frame, 
                                  text=f"Map initialization error: {str(e)}",
                                  font=('Arial', 10),
                                  bg='white',
                                  fg='red')
            error_label.pack(fill='both', expand=True, padx=20, pady=20)
            self.map_widget = None
            print(f"Map error: {e}")
        
        # Status label
        self.map_status_label = tk.Label(main_frame, text="Ready", bg='white', 
                                        font=('Arial', 9), fg='#666666')
        self.map_status_label.pack(fill='x', padx=10, pady=(0, 5))
    
    def refresh_airport_list(self):
        """Refresh the airport dropdown list"""
        self.populate_airport_selector()
        self.map_status_label.config(text="Airport list refreshed")
    
    def on_map_click(self, event):
        """Handle map click for dragging aircraft"""
        if not self.map_widget:
            return
        
        x, y = event.x, event.y
        
        # Check if click is on an aircraft marker
        for marker in self.aircraft_markers:
            try:
                # Get marker position in canvas coordinates
                marker_x, marker_y = self.map_widget.canvas.coords(marker.canvas_circle_id)[:2]
                
                # Check if click is near the marker (within 10 pixels)
                if abs(x - marker_x) < 10 and abs(y - marker_y) < 10:
                    self.dragging_aircraft = marker
                    self.drag_start_pos = (x, y)
                    self.map_status_label.config(text=f"Dragging {marker.aircraft_data['callsign']}")
                    break
            except (AttributeError, IndexError):
                continue
    
    def on_map_drag(self, event):
        """Handle map drag to move aircraft"""
        if not self.dragging_aircraft or not self.map_widget:
            return
        
        x, y = event.x, event.y
        
        # Convert canvas coordinates to geographic coordinates
        try:
            new_lat, new_lon = self.map_widget.canvas_coords_to_geographic(x, y)
            
            # Update aircraft position
            aircraft = self.dragging_aircraft.aircraft_data
            aircraft['lat'] = new_lat
            aircraft['lon'] = new_lon
            
            # Update marker position
            self.dragging_aircraft.set_position(new_lat, new_lon)
            
            # Update aircraft tag position
            self.update_aircraft_tag_position(aircraft)
            
            # Update status
            self.map_status_label.config(
                text=f"Moving {aircraft['callsign']} to {new_lat:.4f}, {new_lon:.4f}"
            )
            
        except Exception as e:
            print(f"Error during drag: {e}")
    
    def on_map_release(self, event):
        """Handle map release after dragging"""
        if self.dragging_aircraft:
            aircraft = self.dragging_aircraft.aircraft_data
            self.map_status_label.config(
                text=f"{aircraft['callsign']} moved to {aircraft['lat']:.4f}, {aircraft['lon']:.4f}"
            )
            
            # Notify parent about position update
            if hasattr(self.parent, 'on_aircraft_position_update'):
                self.parent.on_aircraft_position_update(
                    aircraft['callsign'],
                    f"{aircraft['lat']:.6f}, {aircraft['lon']:.6f}"
                )
            
            self.dragging_aircraft = None
            self.drag_start_pos = None
    
    def update_aircraft_tag_position(self, aircraft):
        """Update position of aircraft tag"""
        if not self.map_widget:
            return
        
        # Find and update the tag
        for tag in self.aircraft_tags:
            if hasattr(tag, 'aircraft_data') and tag.aircraft_data['callsign'] == aircraft['callsign']:
                try:
                    # Position tag slightly above aircraft
                    tag_lat = aircraft['lat'] + 0.01
                    tag_lon = aircraft['lon']
                    tag.set_position(tag_lat, tag_lon)
                    
                    # Update tag text with new position info
                    callsign = aircraft['callsign'][:7].ljust(7)
                    alt = str(aircraft['altitude']).replace('ft', '').strip()
                    alt = alt[:5].rjust(5)
                    spd = aircraft['speed'][:3].rjust(3)
                    hdg = aircraft['heading'][:3].rjust(3)
                    actype = aircraft['type'][:4]
                    
                    tag_text = f"{callsign} {alt} {spd} {hdg} {actype}"
                    tag.set_text(tag_text)
                    
                except Exception as e:
                    print(f"Error updating tag: {e}")
                break
    
    def load_data(self):
        """Load data from parsers"""
        if self.sct_parser:
            sct_data = self.sct_parser.get_data()
            
            # Load boundaries
            self.artcc_high_boundaries = sct_data.get('ARTCC_HIGH', [])
            self.artcc_low_boundaries = sct_data.get('ARTCC_LOW', [])
            
            # Load points
            self.load_sct_points(sct_data)
            
            # Populate airport selector
            self.populate_airport_selector()
        
        if self.rwy_parser:
            rwy_data = self.rwy_parser.get_data()
            self.runway_extensions = rwy_data.get('runways', [])
            self.ils_points = rwy_data.get('ils_data', [])
            
            # Extract runway centerlines from RWY file
            self.extract_runway_centerlines()
        
        # Initial draw
        self.redraw_all()
    
    def extract_runway_centerlines(self):
        """Extract runway centerlines from RWY parser data"""
        self.runway_centerlines = []
        
        if not self.rwy_parser:
            return
        
        # Look for runway definitions in the parsed data
        for runway_data in self.rwy_parser.runways:
            if 'coordinates' in runway_data and runway_data['coordinates']:
                # This is likely a runway centerline
                self.runway_centerlines.append({
                    'name': f"RWY{runway_data.get('number', 'UNK')}",
                    'coordinates': runway_data['coordinates'],
                    'type': 'CENTERLINE'
                })
        
        # Also check for ILS data which often contains runway info
        for ils in self.rwy_parser.ils_data:
            runway_num = ils.get('runway', '')
            if runway_num and ils.get('localizer') and ils.get('glideslope'):
                # Create a simple centerline from glideslope to localizer
                self.runway_centerlines.append({
                    'name': f"ILS{runway_num}",
                    'coordinates': [ils['glideslope'], ils['localizer']],
                    'type': 'ILS_CENTERLINE'
                })
    
    def populate_airport_selector(self):
        """Populate airport dropdown with detailed airport info"""
        airports = []
        
        # Create a detailed list of airports with ICAO and name
        for airport in self.airport_points:
            icao = airport.get('name', '')
            lat = airport.get('lat', 0)
            lon = airport.get('lon', 0)
            
            if icao and len(icao) >= 4:
                # Get additional airport info if available
                airport_info = self.get_airport_info(icao)
                name = airport_info.get('city', '') if airport_info else ''
                
                if name:
                    display_text = f"{icao} - {name}"
                else:
                    display_text = f"{icao} ({lat:.2f}, {lon:.2f})"
                
                airports.append((icao, display_text))
        
        # Sort by ICAO code
        airports.sort(key=lambda x: x[0])
        
        # Update combobox with display text
        display_values = [airport[1] for airport in airports]
        icao_values = [airport[0] for airport in airports]
        
        self.airport_combo['values'] = display_values
        
        # Store mapping for later lookup
        self.airport_display_map = dict(zip(display_values, icao_values))
        
        # Select first airport by default
        if display_values:
            self.airport_combo.set(display_values[0])
            self.selected_airport = icao_values[0]
            self.calculate_entry_fixes()
            self.map_status_label.config(text=f"Selected airport: {self.selected_airport}")
    
    def get_airport_info(self, icao):
        """Get detailed airport information"""
        known_airports = {
            'FAOR': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa'},
            'FACT': {'name': 'Cape Town International', 'city': 'Cape Town', 'country': 'South Africa'},
            'FALE': {'name': 'King Shaka International', 'city': 'Durban', 'country': 'South Africa'},
            'FAGG': {'name': 'George Airport', 'city': 'George', 'country': 'South Africa'},
            'FAPE': {'name': 'Port Elizabeth International', 'city': 'Port Elizabeth', 'country': 'South Africa'},
            'FAEL': {'name': 'East London Airport', 'city': 'East London', 'country': 'South Africa'},
            'FAJS': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa'},
            'FBSK': {'name': 'Sir Seretse Khama International', 'city': 'Gaborone', 'country': 'Botswana'},
            'FVFA': {'name': 'Victoria Falls Airport', 'city': 'Victoria Falls', 'country': 'Zimbabwe'},
            'FQMA': {'name': 'Maputo International', 'city': 'Maputo', 'country': 'Mozambique'},
        }
        
        return known_airports.get(icao, {})
    
    def on_airport_selected(self, event=None):
        """Handle airport selection"""
        display_text = self.airport_var.get()
        if display_text and hasattr(self, 'airport_display_map'):
            icao = self.airport_display_map.get(display_text)
            if icao:
                self.selected_airport = icao
                self.calculate_entry_fixes()
                self.redraw_all()
                self.map_status_label.config(text=f"Selected airport: {icao}")
                
                # Zoom to selected airport
                self.zoom_to_airport(icao)
    
    def zoom_to_airport(self, airport_icao):
        """Zoom map to selected airport"""
        if not self.map_widget:
            return
        
        # Find airport coordinates
        for airport in self.airport_points:
            if airport.get('name') == airport_icao:
                lat = airport.get('lat', -26.145)
                lon = airport.get('lon', 28.234)
                self.map_widget.set_position(lat, lon)
                self.map_widget.set_zoom(12)
                break
    
    def calculate_entry_fixes(self):
        """Calculate fixes within 100NM of selected airport"""
        if not self.selected_airport or not self.airport_points:
            return
        
        # Find airport coordinates
        airport_coords = None
        for airport in self.airport_points:
            if airport.get('name') == self.selected_airport:
                airport_coords = (airport['lat'], airport['lon'])
                break
        
        if not airport_coords:
            return
        
        self.entry_fixes = []
        
        # Check all fixes within 100NM (185.2km) radius
        for fix in self.fix_points:
            fix_coords = (fix['lat'], fix['lon'])
            distance = self.calculate_distance(airport_coords, fix_coords)
            
            if distance <= 100:  # Within 100NM
                self.entry_fixes.append({
                    'name': fix['name'],
                    'lat': fix['lat'],
                    'lon': fix['lon'],
                    'distance_nm': distance
                })
        
        # Sort by distance
        self.entry_fixes.sort(key=lambda x: x['distance_nm'])
        
        self.map_status_label.config(
            text=f"Found {len(self.entry_fixes)} entry fixes within 100NM of {self.selected_airport}"
        )
    
    def calculate_distance(self, coord1, coord2):
        """Calculate distance in nautical miles between two coordinates"""
        import math
        
        # Convert to radians
        lat1, lon1 = map(math.radians, coord1)
        lat2, lon2 = map(math.radians, coord2)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Earth radius in nautical miles (3440.065 NM)
        distance_nm = 3440.065 * c
        
        return distance_nm
    
    def load_sct_points(self, sct_data):
        """Load SCT data points"""
        self.airport_points = []
        for item in sct_data.get('airports', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.airport_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('icao', 'N/A'),
                    'type': 'AIRPORT'
                })
        
        self.fix_points = []
        for item in sct_data.get('fixes', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.fix_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A'),
                    'type': 'FIX'
                })
        
        self.vor_points = []
        for item in sct_data.get('VOR', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.vor_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A'),
                    'type': 'VOR'
                })
        
        self.ndb_points = []
        for item in sct_data.get('NDB', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.ndb_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A'),
                    'type': 'NDB'
                })
    
    def auto_zoom_to_runways(self):
        """Auto-zoom to include runway extensions"""
        if not self.map_widget or not self.runway_extensions:
            return
        
        all_coords = []
        for rwy in self.runway_extensions:
            if 'coordinates' in rwy:
                all_coords.extend(rwy['coordinates'])
        
        if not all_coords:
            return
        
        lats = [c[0] for c in all_coords if c[0] is not None]
        lons = [c[1] for c in all_coords if c[1] is not None]
        
        if lats and lons:
            min_lat = min(lats)
            max_lat = max(lats)
            min_lon = min(lons)
            max_lon = max(lons)
            
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            self.map_widget.set_position(center_lat, center_lon)
            self.map_widget.set_zoom(11)
            self.map_status_label.config(text="Zoomed to runway centerlines")
    
    def add_aircraft(self, aircraft_data):
        """Add an aircraft to the map"""
        if 'position' not in aircraft_data:
            return
        
        try:
            lat, lon = self.parse_position(aircraft_data['position'])
            
            aircraft = {
                'lat': lat,
                'lon': lon,
                'callsign': aircraft_data.get('callsign', 'N/A'),
                'type': aircraft_data.get('type', 'N/A'),
                'altitude': aircraft_data.get('altitude', 'N/A'),
                'route': aircraft_data.get('route', ''),
                'speed': aircraft_data.get('speed', '250'),
                'heading': aircraft_data.get('heading', '000')
            }
            
            self.aircraft_points.append(aircraft)
            self.draw_aircraft(aircraft)
            
        except (ValueError, TypeError) as e:
            print(f"Error adding aircraft: {e}")
    
    def parse_position(self, position_str):
        """Parse position string to lat/lon"""
        if isinstance(position_str, str):
            if ',' in position_str:
                try:
                    lat_str, lon_str = position_str.split(',')
                    return float(lat_str.strip()), float(lon_str.strip())
                except ValueError:
                    position_str = position_str.strip('() ')
                    if ',' in position_str:
                        lat_str, lon_str = position_str.split(',')
                        return float(lat_str.strip()), float(lon_str.strip())
            else:
                import re
                numbers = re.findall(r'-?\d+\.?\d*', position_str)
                if len(numbers) >= 2:
                    return float(numbers[0]), float(numbers[1])
        
        elif isinstance(position_str, (tuple, list)) and len(position_str) >= 2:
            return float(position_str[0]), float(position_str[1])
        
        # Default position if parsing fails
        return -26.145, 28.234
    
    def redraw_all(self):
        """Redraw all map elements"""
        if not self.map_widget:
            return
            
        self.clear_all_drawn_items()
        
        # Draw airspace boundaries
        if self.show_airspace_var.get():
            self.draw_airspace_boundaries()
        
        # Draw SCT points
        self.draw_sct_points()
        
        # Draw runway centerlines
        if self.show_centerlines_var.get():
            self.draw_runway_centerlines()
        
        # Draw runway extensions
        if self.show_ext_var.get():
            self.draw_runway_extensions()
        
        # Draw ILS points
        self.draw_ils_points()
        
        # Draw entry fixes
        if self.show_entry_var.get() and self.entry_fixes:
            self.draw_entry_fixes()
        
        # Highlight selected airport
        if self.selected_airport:
            self.highlight_selected_airport()
        
        # Draw aircraft
        for aircraft in self.aircraft_points:
            self.draw_aircraft(aircraft)
        
        # Update aircraft tags
        self.update_aircraft_tags()
    
    def draw_airspace_boundaries(self):
        """Draw ARTCC boundaries"""
        if not self.map_widget:
            return
            
        # Draw HIGH boundaries in red
        for boundary in self.artcc_high_boundaries:
            segments = boundary.get('segments', [])
            for segment in segments:
                start = segment.get('start')
                end = segment.get('end')
                if start and end:
                    try:
                        path = self.map_widget.set_path(
                            [start, end],
                            color='#ff0000',
                            width=2,
                            name="ARTCC_HIGH"
                        )
                        if path:
                            self.drawn_paths.append(path)
                    except Exception as e:
                        print(f"Error drawing boundary: {e}")
        
        # Draw LOW boundaries in green
        for boundary in self.artcc_low_boundaries:
            segments = boundary.get('segments', [])
            for segment in segments:
                start = segment.get('start')
                end = segment.get('end')
                if start and end:
                    try:
                        path = self.map_widget.set_path(
                            [start, end],
                            color='#00aa00',
                            width=1,
                            name="ARTCC_LOW"
                        )
                        if path:
                            self.drawn_paths.append(path)
                    except Exception as e:
                        print(f"Error drawing boundary: {e}")
    
    def draw_sct_points(self):
        """Draw SCT points (airports, fixes, VOR, NDB)"""
        if not self.map_widget:
            return
        
        # Clear previous airport markers
        for marker in self.airport_markers:
            try:
                marker.delete()
            except:
                pass
        self.airport_markers = []
            
        # Draw airports with better markers
        for point in self.airport_points:
            try:
                # Use a special airport icon
                icao = point['name']
                airport_info = self.get_airport_info(icao)
                display_name = airport_info.get('name', icao) if airport_info else icao
                
                marker = self.map_widget.set_marker(
                    point['lat'], point['lon'],
                    text=f"✈ {icao}",
                    marker_color_outside='#0088ff',
                    marker_color_circle='white',
                    text_color='#0066cc',
                    font=('Arial', 9, 'bold'),
                    text_offset_y=10
                )
                
                if marker:
                    self.airport_markers.append(marker)
                    self.drawn_markers.append(marker)
                    
                    # Add airport name as a separate marker below
                    name_marker = self.map_widget.set_marker(
                        point['lat'] - 0.001, point['lon'],
                        text=display_name[:20],
                        text_color='#333333',
                        font=('Arial', 8),
                        marker_color_circle='white',
                        marker_color_outside='white',
                        text_offset_y=5
                    )
                    if name_marker:
                        self.airport_markers.append(name_marker)
                        self.drawn_markers.append(name_marker)
                        
            except Exception as e:
                print(f"Error drawing airport: {e}")
        
        # Draw fixes as small black dots
        for point in self.fix_points:
            try:
                marker = self.map_widget.set_marker(
                    point['lat'], point['lon'],
                    text=point['name'],
                    marker_color_outside='black',
                    marker_color_circle='black',
                    text_color='black',
                    font=('Arial', 7),
                    marker_color_circle_radius=2
                )
                if marker:
                    self.drawn_markers.append(marker)
            except Exception as e:
                print(f"Error drawing fix: {e}")
    
    def draw_runway_centerlines(self):
        """Draw runway centerlines from RWY file"""
        if not self.map_widget:
            return
        
        for centerline in self.runway_centerlines:
            try:
                if 'coordinates' in centerline and len(centerline['coordinates']) >= 2:
                    # Draw centerline in blue
                    path = self.map_widget.set_path(
                        centerline['coordinates'],
                        color='#0000ff',
                        width=2,
                        name=centerline['name']
                    )
                    if path:
                        self.runway_line_markers.append(path)
                        self.drawn_paths.append(path)
                    
                    # Add runway label
                    if len(centerline['coordinates']) >= 2:
                        mid_idx = len(centerline['coordinates']) // 2
                        mid_lat = centerline['coordinates'][mid_idx][0]
                        mid_lon = centerline['coordinates'][mid_idx][1]
                        
                        marker = self.map_widget.set_marker(
                            mid_lat, mid_lon,
                            text=centerline['name'],
                            text_color='#0000ff',
                            font=('Arial', 8, 'bold'),
                            marker_color_circle='white',
                            marker_color_outside='white'
                        )
                        if marker:
                            self.drawn_markers.append(marker)
                            
            except Exception as e:
                print(f"Error drawing runway centerline: {e}")
    
    def draw_entry_fixes(self):
        """Draw entry fixes within 100NM radius"""
        if not self.map_widget:
            return
            
        for fix in self.entry_fixes:
            try:
                # Draw as orange diamond
                marker = self.map_widget.set_marker(
                    fix['lat'], fix['lon'],
                    text=fix['name'],
                    marker_color_outside='#ff9900',
                    marker_color_circle='white',
                    text_color='#cc6600',
                    font=('Arial', 9, 'bold'),
                    marker_color_circle_radius=4
                )
                if marker:
                    self.entry_fix_markers.append(marker)
                    
                # Add distance label
                marker = self.map_widget.set_marker(
                    fix['lat'] - 0.002, fix['lon'],
                    text=f"{fix['distance_nm']:.0f}NM",
                    text_color='#996600',
                    font=('Arial', 7),
                    marker_color_circle='white',
                    marker_color_outside='white'
                )
                if marker:
                    self.entry_fix_markers.append(marker)
                    
            except Exception as e:
                print(f"Error drawing entry fix: {e}")
    
    def highlight_selected_airport(self):
        """Highlight the selected airport"""
        if not self.map_widget:
            return
            
        for airport in self.airport_points:
            if airport.get('name') == self.selected_airport:
                try:
                    # Draw a larger circle around selected airport
                    marker = self.map_widget.set_marker(
                        airport['lat'], airport['lon'],
                        text=f"★ {airport['name']}",
                        marker_color_outside='#ff0000',
                        marker_color_circle='#ffcccc',
                        text_color='#cc0000',
                        font=('Arial', 10, 'bold'),
                        marker_color_circle_radius=8
                    )
                    if marker:
                        self.drawn_markers.append(marker)
                    
                    # Draw 100NM radius circle
                    self.draw_radius_circle(airport['lat'], airport['lon'], 100)
                    
                except Exception as e:
                    print(f"Error highlighting airport: {e}")
                break
    
    def draw_radius_circle(self, center_lat, center_lon, radius_nm):
        """Draw a circle with given radius in NM"""
        if not self.map_widget:
            return
            
        import math
        
        points = []
        for angle in range(0, 360, 10):
            angle_rad = math.radians(angle)
            
            lat_offset = (radius_nm / 60) * math.cos(angle_rad)
            lon_offset = (radius_nm / (60 * math.cos(math.radians(center_lat)))) * math.sin(angle_rad)
            
            point_lat = center_lat + lat_offset
            point_lon = center_lon + lon_offset
            points.append((point_lat, point_lon))
        
        points.append(points[0])
        
        try:
            path = self.map_widget.set_path(
                points,
                color='#ff9900',
                width=1,
                name=f"100NM_Radius"
            )
            if path:
                self.drawn_paths.append(path)
        except Exception as e:
            print(f"Error drawing radius circle: {e}")
    
    def draw_runway_extensions(self):
        """Draw runway extended centerlines"""
        if not self.map_widget:
            return
            
        for rwy in self.runway_extensions:
            if 'coordinates' in rwy and rwy['coordinates']:
                try:
                    # Draw extended centerline in cyan
                    path = self.map_widget.set_path(
                        rwy['coordinates'],
                        color='#00ffff',
                        width=2,
                        name=f"RWY_{rwy.get('number', 'UNK')}"
                    )
                    if path:
                        self.extended_lines.append(path)
                        self.drawn_paths.append(path)
                    
                    # Add runway number label
                    if len(rwy['coordinates']) >= 2:
                        mid_idx = len(rwy['coordinates']) // 2
                        mid_lat = rwy['coordinates'][mid_idx][0]
                        mid_lon = rwy['coordinates'][mid_idx][1]
                        
                        marker = self.map_widget.set_marker(
                            mid_lat, mid_lon,
                            text=f"RWY {rwy.get('number', 'UNK')}",
                            text_color='#00aaaa',
                            font=('Arial', 8),
                            marker_color_circle='white',
                            marker_color_outside='white'
                        )
                        if marker:
                            self.drawn_markers.append(marker)
                            
                except Exception as e:
                    print(f"Error drawing runway extension: {e}")
    
    def draw_ils_points(self):
        """Draw ILS localizer and glideslope points"""
        if not self.map_widget:
            return
            
        for ils in self.ils_points:
            try:
                # Draw localizer as green triangle
                loc_lat, loc_lon = ils['localizer']
                marker = self.map_widget.set_marker(
                    loc_lat, loc_lon,
                    text=f"LOC {ils['name']}",
                    marker_color_outside='#00ff00',
                    marker_color_circle='white',
                    text_color='#008800',
                    font=('Arial', 8),
                    marker_color_circle_radius=4
                )
                if marker:
                    self.drawn_markers.append(marker)
                
                # Draw glideslope as blue circle
                gs_lat, gs_lon = ils['glideslope']
                marker = self.map_widget.set_marker(
                    gs_lat, gs_lon,
                    text=f"GS {ils['name']}",
                    marker_color_outside='#0000ff',
                    marker_color_circle='white',
                    text_color='#000088',
                    font=('Arial', 8),
                    marker_color_circle_radius=3
                )
                if marker:
                    self.drawn_markers.append(marker)
                
                # Draw line between them
                path = self.map_widget.set_path(
                    [ils['glideslope'], ils['localizer']],
                    color='#888888',
                    width=1,
                    name=f"ILS_{ils['name']}"
                )
                if path:
                    self.drawn_paths.append(path)
                    
            except Exception as e:
                print(f"Error drawing ILS: {e}")
    
    def draw_aircraft(self, aircraft):
        """Draw an aircraft on the map"""
        if not self.map_widget:
            return
        
        try:
            # Create aircraft marker (small airplane symbol)
            marker = self.map_widget.set_marker(
                aircraft['lat'], aircraft['lon'],
                text="✈",
                marker_color_outside='#ff0000',
                marker_color_circle='white',
                text_color='#000000',
                font=('Arial', 12),
                text_offset_y=0
            )
            
            if marker:
                # Store aircraft data with marker for dragging
                marker.aircraft_data = aircraft
                self.aircraft_markers.append(marker)
                
                # Create aircraft tag if enabled
                if self.show_tags_var.get():
                    self.create_aircraft_tag(aircraft)
                    
        except Exception as e:
            print(f"Error drawing aircraft: {e}")
    
    def create_aircraft_tag(self, aircraft):
        """Create tag for aircraft"""
        if not self.map_widget:
            return
        
        try:
            # Position tag slightly above aircraft
            tag_lat = aircraft['lat'] + 0.01
            tag_lon = aircraft['lon']
            
            # Format tag text
            callsign = aircraft['callsign'][:7].ljust(7)
            alt = str(aircraft['altitude']).replace('ft', '').strip()
            alt = alt[:5].rjust(5)
            spd = aircraft['speed'][:3].rjust(3)
            hdg = aircraft['heading'][:3].rjust(3)
            actype = aircraft['type'][:4]
            
            tag_text = f"{callsign} {alt} {spd} {hdg} {actype}"
            
            tag = self.map_widget.set_marker(
                tag_lat, tag_lon,
                text=tag_text,
                text_color='#000000',
                font=('Arial', 8, 'bold'),
                marker_color_circle='white',
                marker_color_outside='white',
                text_offset_y=0
            )
            
            if tag:
                tag.aircraft_data = aircraft
                self.aircraft_tags.append(tag)
                
        except Exception as e:
            print(f"Error creating aircraft tag: {e}")
    
    def update_aircraft_tags(self):
        """Update visibility of aircraft tags"""
        for tag in self.aircraft_tags:
            try:
                if self.show_tags_var.get():
                    tag.set_text(tag.aircraft_data['callsign'])
                else:
                    tag.set_text("")
            except:
                pass
    
    def toggle_tags(self):
        """Toggle aircraft tags visibility"""
        self.update_aircraft_tags()
    
    def clear_all_drawn_items(self):
        """Clear all drawn items from map"""
        # Clear paths
        for path in self.drawn_paths:
            try:
                path.delete()
            except:
                pass
        self.drawn_paths = []
        
        # Clear markers
        for marker in self.drawn_markers:
            try:
                marker.delete()
            except:
                pass
        self.drawn_markers = []
        
        # Clear aircraft markers
        for marker in self.aircraft_markers:
            try:
                marker.delete()
            except:
                pass
        self.aircraft_markers = []
        
        # Clear aircraft tags
        for tag in self.aircraft_tags:
            try:
                tag.delete()
            except:
                pass
        self.aircraft_tags = []
        
        # Clear extended lines
        for line in self.extended_lines:
            try:
                line.delete()
            except:
                pass
        self.extended_lines = []
        
        # Clear entry fix markers
        for marker in self.entry_fix_markers:
            try:
                marker.delete()
            except:
                pass
        self.entry_fix_markers = []
        
        # Clear runway line markers
        for marker in self.runway_line_markers:
            try:
                marker.delete()
            except:
                pass
        self.runway_line_markers = []
        
        # Clear airport markers
        for marker in self.airport_markers:
            try:
                marker.delete()
            except:
                pass
        self.airport_markers = []
    
    def clear_aircraft(self):
        """Clear all aircraft from map"""
        self.aircraft_points = []
        self.clear_all_drawn_items()
        self.redraw_all()
    
    def get_entry_fixes(self):
        """Get entry fixes for current airport"""
        return self.entry_fixes
    
    def get_selected_airport(self):
        """Get currently selected airport"""
        return self.selected_airport