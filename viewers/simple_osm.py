import tkinter as tk
from tkinter import ttk
try:
    import tkintermapview
    HAS_MAPVIEW = True
except ImportError:
    HAS_MAPVIEW = False

class SimpleOSMViewer:
    def __init__(self, parent, ese_parser, sct_parser=None):
        self.parent = parent
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        self.markers = []
        
        self.setup_ui()
        if HAS_MAPVIEW:
            self.load_data_to_map()
        else:
            self.show_install_message()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        control_frame = tk.Frame(main_frame, bg='white', height=50)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)
        
        title_label = tk.Label(
            control_frame,
            text="OpenStreetMap Viewer",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(side='left', padx=10, pady=10)
        
        if HAS_MAPVIEW:
            self.map_widget = tkintermapview.TkinterMapView(main_frame, width=800, height=600, corner_radius=0)
            self.map_widget.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
            self.map_widget.set_position(51.5074, -0.1278)
            self.map_widget.set_zoom(6)
        else:
            error_frame = tk.Frame(main_frame, bg='#ffebee', height=600)
            error_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            
            error_label = tk.Label(
                error_frame,
                text="tkintermapview not installed!\n\nPlease install it using:\npip install tkintermapview Pillow\n\nThen restart the application.",
                font=('Arial', 12),
                bg='#ffebee',
                fg='#c62828',
                justify='center'
            )
            error_label.pack(expand=True)
        
        self.legend_frame = tk.Frame(main_frame, bg='white', relief='ridge', borderwidth=1)
        self.legend_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        legend_label = tk.Label(
            self.legend_frame,
            text="Legend:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        legend_label.pack(side='left', padx=10, pady=5)
        
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        labels = ['TWR', 'APP/DEP', 'CTR', 'ATIS', 'Other']
        
        for color, label in zip(colors, labels):
            color_box = tk.Frame(self.legend_frame, bg=color, width=20, height=20)
            color_box.pack(side='left', padx=5, pady=5)
            color_box.pack_propagate(False)
            
            lbl = tk.Label(
                self.legend_frame,
                text=label,
                font=('Arial', 9),
                bg='white'
            )
            lbl.pack(side='left', padx=(0, 10), pady=5)
    
    def load_data_to_map(self):
        if not HAS_MAPVIEW:
            return
            
        positions = self.ese_parser.get_positions()
        positions_count = len(positions)
        
        if positions_count > 0:
            avg_lat = 0
            avg_lon = 0
            valid_positions = 0
            
            for position in positions:
                if 'coordinates' in position and position['coordinates']:
                    lat = None
                    lon = None
                    
                    for coord in position['coordinates']:
                        parsed = self.parse_coordinate(coord)
                        if parsed:
                            if parsed[0] is not None:
                                lat = parsed[0]
                            if parsed[1] is not None:
                                lon = parsed[1]
                    
                    if lat is not None and lon is not None:
                        valid_positions += 1
                        avg_lat += lat
                        avg_lon += lon
                        
                        marker_color = self.get_position_color(position['type'])
                        marker = self.map_widget.set_marker(lat, lon, 
                                                          text=f"{position['callsign']}\n{position['type']}",
                                                          marker_color_outside=marker_color,
                                                          marker_color_circle='white',
                                                          text_color='black')
                        self.markers.append((marker, position))
            
            if valid_positions > 0:
                avg_lat /= valid_positions
                avg_lon /= valid_positions
                self.map_widget.set_position(avg_lat, avg_lon)
                self.map_widget.set_zoom(8)
        
        if self.sct_parser:
            sct_data = self.sct_parser.get_data()
            airports = sct_data.get('airports', [])
            
            if airports:
                for airport in airports[:50]:
                    if isinstance(airport, dict) and 'latitude' in airport and 'longitude' in airport:
                        lat = airport['latitude']
                        lon = airport['longitude']
                        if lat is not None and lon is not None:
                            self.map_widget.set_marker(lat, lon,
                                                      text=f"APT: {airport.get('icao', 'N/A')}",
                                                      marker_color_outside='green',
                                                      text_color='white')
        
        stats_text = f"Loaded: {positions_count} controller positions"
        if self.sct_parser:
            sct_data = self.sct_parser.get_data()
            stats_text += f" | SCT: {len(sct_data.get('airports', []))} airports, {len(sct_data.get('fixes', []))} fixes"
        
        stats_frame = tk.Frame(self.parent, bg='white')
        stats_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        stats_label = tk.Label(
            stats_frame,
            text=stats_text,
            font=('Arial', 10),
            bg='white',
            fg='#34495e'
        )
        stats_label.pack()
    
    def show_install_message(self):
        pass
    
    def get_position_color(self, pos_type):
        pos_type = pos_type.upper()
        if pos_type == 'TWR':
            return 'red'
        elif pos_type in ['APP', 'DEP']:
            return 'blue'
        elif pos_type == 'CTR':
            return 'green'
        elif pos_type == 'ATIS':
            return 'purple'
        elif pos_type == 'GND':
            return 'darkorange'
        elif pos_type == 'DEL':
            return 'brown'
        elif pos_type == 'FSS':
            return 'cyan'
        else:
            return 'gray'
    
    def parse_coordinate(self, coord_str):
        import re
        
        if not coord_str:
            return None
        
        coord_str = coord_str.strip().upper()
        
        lat_match = re.match(r'^([NS])(\d+)\.(\d+)\.(\d+)\.(\d+)$', coord_str)
        lon_match = re.match(r'^([EW])(\d+)\.(\d+)\.(\d+)\.(\d+)$', coord_str)
        
        if lat_match:
            direction = lat_match.group(1)
            degrees = float(lat_match.group(2))
            minutes = float(lat_match.group(3))
            seconds = float(lat_match.group(4))
            decimal = float(lat_match.group(5)) / 1000.0
            
            lat = degrees + minutes/60 + (seconds + decimal)/3600
            if direction == 'S':
                lat = -lat
            return (lat, None)
        
        if lon_match:
            direction = lon_match.group(1)
            degrees = float(lon_match.group(2))
            minutes = float(lon_match.group(3))
            seconds = float(lon_match.group(4))
            decimal = float(lon_match.group(5)) / 1000.0
            
            lon = degrees + minutes/60 + (seconds + decimal)/3600
            if direction == 'W':
                lon = -lon
            return (None, lon)
        
        return None