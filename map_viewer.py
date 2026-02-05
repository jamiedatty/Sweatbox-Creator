"""
Map Viewer Module
Displays positions on a simple canvas-based map
"""
import tkinter as tk
from tkinter import ttk
import re

class MapViewer:
    def __init__(self, parent, ese_parser):
        self.parent = parent
        self.ese_parser = ese_parser
        self.positions = ese_parser.get_positions()
        
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.setup_ui()
        self.draw_map()
    
    def setup_ui(self):
        self.map_frame = tk.Frame(self.parent, bg='white')
        self.map_frame.pack(fill='both', expand=True)
        
        info_label = tk.Label(
            self.map_frame,
            text=f"Displaying {len(self.positions)} controller positions",
            font=('Arial', 10),
            bg='
            pady=10
        )
        info_label.pack(fill='x')
        
        self.canvas = tk.Canvas(
            self.map_frame,
            bg='
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.canvas.bind('<ButtonPress-1>', self.start_pan)
        self.canvas.bind('<B1-Motion>', self.pan)
        self.canvas.bind('<MouseWheel>', self.zoom_map)
        
        legend_frame = tk.Frame(self.map_frame, bg='
        legend_frame.pack(fill='x', pady=5)
        
        tk.Label(
            legend_frame,
            text="● Tower/Ground  ● Approach  ● Center  ● ATIS/Other",
            font=('Arial', 9),
            bg='
            fg='
        ).pack()
    
    def draw_map(self):
        self.canvas.delete('all')
        
        width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 800
        height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 600
        
        coords_data = []
        for position in self.positions:
            coords = self.extract_coordinates(position)
            if coords:
                coords_data.append({
                    'lat': coords[0],
                    'lon': coords[1],
                    'name': position['callsign'],
                    'type': position['type'],
                    'frequency': position['frequency']
                })
        
        if not coords_data:
            self.canvas.create_text(
                width // 2,
                height // 2,
                text="No coordinate data available in ESE file",
                font=('Arial', 14),
                fill='white'
            )
            return
        
        lats = [c['lat'] for c in coords_data]
        lons = [c['lon'] for c in coords_data]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        
        if lat_range == 0:
            lat_range = 1
        if lon_range == 0:
            lon_range = 1
        
        padding = 0.1
        min_lat -= lat_range * padding
        max_lat += lat_range * padding
        min_lon -= lon_range * padding
        max_lon += lon_range * padding
        
        self.draw_grid(width, height, min_lat, max_lat, min_lon, max_lon)
        
        for coord in coords_data:
            x = ((coord['lon'] - min_lon) / (max_lon - min_lon)) * width
            y = height - ((coord['lat'] - min_lat) / (max_lat - min_lat)) * height
            
            color = self.get_position_color(coord['type'])
            
            size = 6
            self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=color,
                outline='white',
                width=1,
                tags='position'
            )
            
            self.canvas.create_text(
                x + 10, y,
                text=coord['name'],
                font=('Arial', 8, 'bold'),
                fill='white',
                anchor='w',
                tags='label'
            )
            
            item_id = self.canvas.find_closest(x, y)[0]
            self.canvas.tag_bind(
                item_id,
                '<Enter>',
                lambda e, c=coord: self.show_tooltip(e, c)
            )
            self.canvas.tag_bind(item_id, '<Leave>', self.hide_tooltip)
    
    def draw_grid(self, width, height, min_lat, max_lat, min_lon, max_lon):
        for i in range(5):
            y = (i / 4) * height
            lat = max_lat - (i / 4) * (max_lat - min_lat)
            self.canvas.create_line(
                0, y, width, y,
                fill='
                dash=(2, 4)
            )
            self.canvas.create_text(
                10, y,
                text=f"{lat:.1f}°",
                font=('Arial', 8),
                fill='
                anchor='nw'
            )
        
        for i in range(5):
            x = (i / 4) * width
            lon = min_lon + (i / 4) * (max_lon - min_lon)
            self.canvas.create_line(
                x, 0, x, height,
                fill='
                dash=(2, 4)
            )
            self.canvas.create_text(
                x, height - 10,
                text=f"{lon:.1f}°",
                font=('Arial', 8),
                fill='
                anchor='sw'
            )
    
    def get_position_color(self, pos_type):
        pos_type = pos_type.upper()
        
        if pos_type in ['TWR', 'GND', 'DEL']:
            return 'red'
        elif pos_type in ['APP', 'DEP']:
            return 'blue'
        elif pos_type == 'CTR':
            return 'green'
        else:
            return 'yellow'
    
    def extract_coordinates(self, position):
        if 'coordinates' not in position or not position['coordinates']:
            return None
        
        lat = None
        lon = None
        
        for coord_str in position['coordinates']:
            parsed = self.parse_coordinate(coord_str)
            if parsed:
                if parsed[0] is not None:
                    lat = parsed[0]
                if parsed[1] is not None:
                    lon = parsed[1]
        
        if lat is not None and lon is not None:
            return (lat, lon)
        return None
    
    def parse_coordinate(self, coord_str):
        if not coord_str:
            return None
        
        coord_str = coord_str.strip().upper()
        
        lat_match = re.match(r'^([NS])(\d+)\.(\d+)\.(\d+)\.(\d+)$', coord_str)
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
        
        lon_match = re.match(r'^([EW])(\d+)\.(\d+)\.(\d+)\.(\d+)$', coord_str)
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
    
    def show_tooltip(self, event, coord):
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        label = tk.Label(
            self.tooltip,
            text=f"{coord['name']}\nType: {coord['type']}\nFreq: {coord['frequency']}",
            background='
            foreground='white',
            relief='solid',
            borderwidth=1,
            font=('Arial', 9),
            padx=5,
            pady=5
        )
        label.pack()
    
    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
    
    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def pan(self, event):
        pass
    
    def zoom_map(self, event):
        pass