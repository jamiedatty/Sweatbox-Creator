"""
Folium Map Viewer Module
Creates interactive maps using folium
"""
import folium
from folium import plugins
import tempfile
import os
import webbrowser
from typing import List, Dict, Tuple
import tkinter as tk

class FoliumMapViewer:
    def __init__(self, ese_parser, sct_parser=None):
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        self.map_file = None
        self.m = None
        
        self.create_map()
    
    def create_map(self):
        # Calculate center from all coordinates
        all_coords = self.get_all_coordinates()
        
        if all_coords:
            lats = [c['lat'] for c in all_coords]
            lons = [c['lon'] for c in all_coords]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
        else:
            center_lat, center_lon = 50.0, 10.0  # Default center
        
        # Create map
        self.m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Add tile layers
        folium.TileLayer('OpenStreetMap').add_to(self.m)
        folium.TileLayer('CartoDB positron').add_to(self.m)
        folium.TileLayer('CartoDB dark_matter').add_to(self.m)
        
        # Add features
        self.add_airspace()
        self.add_controllers()
        self.add_airports()
        self.add_navaids()
        
        # Add controls
        folium.LayerControl().add_to(self.m)
        plugins.Fullscreen().add_to(self.m)
        plugins.MiniMap().add_to(self.m)
        
        # Add legend
        self.add_legend()
        
        # Save map
        self.save_map()
    
    def get_all_coordinates(self):
        coords = []
        
        # Add controller positions
        for position in self.ese_parser.get_positions():
            coord = self.extract_co