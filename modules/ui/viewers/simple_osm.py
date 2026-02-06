import tkinter as tk
import os
import shutil
import time
from tkinter import messagebox
from tkintermapview import TkinterMapView

class SimpleOSMViewer:
    def __init__(self, parent, ese_parser, sct_parser=None):
        self.parent = parent
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        
        # Store data
        self.artcc_high_boundaries = []
        self.artcc_low_boundaries = []
        self.airport_points = []
        self.fix_points = []
        self.vor_points = []
        self.ndb_points = []
        
        # Store drawn items
        self.drawn_paths = []
        self.drawn_markers = []
        
        # Zoom tracking
        self.last_zoom_level = None
        self.min_zoom_for_boundaries = 7  # Lower zoom level for boundaries
        self.boundaries_visible = True  # Start with boundaries visible
        
        # Performance tracking
        self.load_time = 0
        self.draw_time = 0
        
        # Auto-zoom tracking
        self.auto_zoom_coords = []
        
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
            text="SCT File Viewer (Optimized)",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(side='left', padx=10, pady=5)
        
        # Performance label
        self.perf_label = tk.Label(
            control_frame,
            text="",
            font=('Arial', 9),
            bg='white',
            fg='#666666'
        )
        self.perf_label.pack(side='right', padx=10, pady=5)
        
        # Map widget
        self.map_widget = TkinterMapView(main_frame, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)
        
        # Controls frame
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Display controls
        display_frame = tk.Frame(controls_frame, bg='white')
        display_frame.pack(fill='x', pady=(0, 5))
        
        # Toggle variables
        self.artcc_high_var = tk.BooleanVar(value=True)
        self.artcc_low_var = tk.BooleanVar(value=True)
        self.airports_var = tk.BooleanVar(value=False)
        self.fixes_var = tk.BooleanVar(value=False)
        self.vor_var = tk.BooleanVar(value=False)
        self.ndb_var = tk.BooleanVar(value=False)
        
        # Checkbuttons in rows
        row1 = tk.Frame(display_frame, bg='white')
        row1.pack(fill='x', pady=2)
        
        tk.Checkbutton(row1, text="ARTCC HIGH", variable=self.artcc_high_var, 
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        tk.Checkbutton(row1, text="ARTCC LOW", variable=self.artcc_low_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        tk.Checkbutton(row1, text="Airports", variable=self.airports_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        
        row2 = tk.Frame(display_frame, bg='white')
        row2.pack(fill='x', pady=2)
        
        tk.Checkbutton(row2, text="Fixes (Black X)", variable=self.fixes_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        tk.Checkbutton(row2, text="VOR (△)", variable=self.vor_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        tk.Checkbutton(row2, text="NDB (□)", variable=self.ndb_var,
                      bg='white', font=('Arial', 9), command=self.redraw_all).pack(side='left', padx=5)
        
        # Action buttons
        action_frame = tk.Frame(controls_frame, bg='white')
        action_frame.pack(fill='x', pady=5)
        
        tk.Button(action_frame, text="Show All", font=('Arial', 9), bg='#3498db', fg='white',
                 command=self.show_all).pack(side='left', padx=2)
        tk.Button(action_frame, text="Hide All", font=('Arial', 9), bg='#e74c3c', fg='white',
                 command=self.hide_all).pack(side='left', padx=2)
        tk.Button(action_frame, text="Auto Zoom", font=('Arial', 9), bg='#2ecc71', fg='white',
                 command=self.auto_zoom).pack(side='left', padx=2)
        
        # Cache control button
        tk.Button(action_frame, text="Clear Cache", font=('Arial', 9), bg='#e67e22', fg='white',
                 command=self.clear_cache).pack(side='left', padx=2)
        
        # Boundary info label
        self.boundary_info_label = tk.Label(
            controls_frame,
            text="",
            font=('Arial', 9),
            bg='white',
            fg='#666666',
            wraplength=1000
        )
        self.boundary_info_label.pack(pady=(5, 0))
    
    def clear_cache(self):
        """Clear the cache directory"""
        cache_dir = "cache"
        if os.path.exists(cache_dir):
            try:
                # Count files before deletion
                cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
                file_count = len(cache_files)
                
                # Delete the cache directory
                shutil.rmtree(cache_dir)
                
                # Recreate empty directory
                os.makedirs(cache_dir)
                
                # Show confirmation message
                messagebox.showinfo("Cache Cleared", 
                                  f"Successfully cleared cache.\nDeleted {file_count} cache files.")
                
                # Update UI
                self.perf_label.config(text="Cache cleared")
                print(f"Cache cleared: {file_count} files deleted")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear cache:\n{str(e)}")
        else:
            messagebox.showinfo("Cache", "Cache directory does not exist.")
    
    def load_data(self):
        start_time = time.time()
        
        if not self.sct_parser:
            self.boundary_info_label.config(text="No SCT file loaded")
            return
        
        sct_data = self.sct_parser.get_data()
        
        # Load ARTCC boundaries from cache
        self.artcc_high_boundaries = sct_data.get('ARTCC_HIGH', [])
        self.artcc_low_boundaries = sct_data.get('ARTCC_LOW', [])
        
        # Load points (always fresh)
        self.airport_points = []
        for item in sct_data.get('airports', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.airport_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('icao', 'N/A')
                })
                self.auto_zoom_coords.append((lat, lon))
        
        self.fix_points = []
        for item in sct_data.get('fixes', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.fix_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A')
                })
                self.auto_zoom_coords.append((lat, lon))
        
        self.vor_points = []
        for item in sct_data.get('VOR', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.vor_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A')
                })
                self.auto_zoom_coords.append((lat, lon))
        
        self.ndb_points = []
        for item in sct_data.get('NDB', []):
            lat = item.get('latitude')
            lon = item.get('longitude')
            if lat is not None and lon is not None:
                self.ndb_points.append({
                    'lat': lat,
                    'lon': lon,
                    'name': item.get('name', 'N/A')
                })
                self.auto_zoom_coords.append((lat, lon))
        
        # Add boundary coordinates for auto-zoom
        for boundary in self.artcc_high_boundaries:
            for segment in boundary.get('segments', []):
                start = segment.get('start')
                end = segment.get('end')
                if start:
                    self.auto_zoom_coords.append(start)
                if end:
                    self.auto_zoom_coords.append(end)
        
        for boundary in self.artcc_low_boundaries:
            for segment in boundary.get('segments', []):
                start = segment.get('start')
                end = segment.get('end')
                if start:
                    self.auto_zoom_coords.append(start)
                if end:
                    self.auto_zoom_coords.append(end)
        
        # Update boundary info
        total_high = len(self.artcc_high_boundaries)
        total_low = len(self.artcc_low_boundaries)
        total_segments_high = sum(len(b.get('segments', [])) for b in self.artcc_high_boundaries)
        total_segments_low = sum(len(b.get('segments', [])) for b in self.artcc_low_boundaries)
        
        self.load_time = time.time() - start_time
        
        self.boundary_info_label.config(
            text=f"ARTCC HIGH: {total_high} boundaries ({total_segments_high} segments) | " +
                 f"ARTCC LOW: {total_low} boundaries ({total_segments_low} segments) | " +
                 f"Fixes: {len(self.fix_points)} | VOR: {len(self.vor_points)} | NDB: {len(self.ndb_points)}"
        )
        
        # Auto-zoom to fit all data
        self.auto_zoom()
        
        # Draw initial data
        self.redraw_all()
    
    def auto_zoom(self):
        """Auto-zoom to fit all loaded data"""
        if not self.auto_zoom_coords:
            return
        
        lats = [c[0] for c in self.auto_zoom_coords if c[0] is not None]
        lons = [c[1] for c in self.auto_zoom_coords if c[1] is not None]
        
        if not lats or not lons:
            return
        
        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)
        
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        max_span = max(lat_span, lon_span)
        
        # Calculate zoom level
        if max_span < 0.1:
            zoom = 13
        elif max_span < 0.5:
            zoom = 11
        elif max_span < 1:
            zoom = 10
        elif max_span < 2:
            zoom = 9
        elif max_span < 5:
            zoom = 8
        elif max_span < 10:
            zoom = 7
        elif max_span < 20:
            zoom = 6
        elif max_span < 40:
            zoom = 5
        else:
            zoom = 4
        
        self.map_widget.set_position(center_lat, center_lon)
        self.map_widget.set_zoom(zoom)
        
        # Update performance label
        self.perf_label.config(text=f"Zoom: {zoom} | Load: {self.load_time:.2f}s | Draw: {self.draw_time:.2f}s")
    
    def redraw_all(self):
        """Redraw everything based on current visibility settings"""
        draw_start_time = time.time()
        self.clear_all_drawn_items()
        
        # Check current zoom level
        current_zoom = self.map_widget.zoom if hasattr(self.map_widget, 'zoom') else 10
        
        # OPTIMIZATION: Draw boundaries in batches
        if (self.artcc_high_var.get() or self.artcc_low_var.get()):
            self.draw_boundaries_optimized()
        
        # Always draw points regardless of zoom
        # Draw airports
        if self.airport_points and self.airports_var.get():
            self.draw_airports()
        
        # Draw fixes as BLACK X only (no name)
        if self.fix_points and self.fixes_var.get():
            self.draw_fixes()
        
        # Draw VOR as magenta triangle with name above
        if self.vor_points and self.vor_var.get():
            self.draw_vors()
        
        # Draw NDB as yellow square with name above
        if self.ndb_points and self.ndb_var.get():
            self.draw_ndbs()
        
        self.draw_time = time.time() - draw_start_time
        
        # Update performance label
        self.perf_label.config(text=f"Zoom: {current_zoom} | Load: {self.load_time:.2f}s | Draw: {self.draw_time:.2f}s")
    
    def draw_boundaries_optimized(self):
        """Optimized boundary drawing - batch similar boundaries"""
        try:
            # Group HIGH boundaries
            if self.artcc_high_var.get():
                high_coords = []
                for boundary in self.artcc_high_boundaries:
                    segments = boundary.get('segments', [])
                    for segment in segments:
                        start = segment.get('start')
                        end = segment.get('end')
                        if start and end:
                            high_coords.extend([start, end])
                
                # Draw all HIGH boundaries as one path if we have coordinates
                if high_coords:
                    # Create a continuous path (even though segments are separate, this is faster)
                    path = self.map_widget.set_path(
                        high_coords,
                        color='#ff0000',
                        width=2,
                        name="ARTCC_HIGH_ALL"
                    )
                    if path:
                        self.drawn_paths.append(path)
            
            # Group LOW boundaries
            if self.artcc_low_var.get():
                low_coords = []
                for boundary in self.artcc_low_boundaries:
                    segments = boundary.get('segments', [])
                    for segment in segments:
                        start = segment.get('start')
                        end = segment.get('end')
                        if start and end:
                            low_coords.extend([start, end])
                
                # Draw all LOW boundaries as one path
                if low_coords:
                    path = self.map_widget.set_path(
                        low_coords,
                        color='#00aa00',
                        width=1,
                        name="ARTCC_LOW_ALL"
                    )
                    if path:
                        self.drawn_paths.append(path)
                        
        except Exception as e:
            print(f"Error drawing optimized boundaries: {e}")
            # Fall back to individual segment drawing
            self.draw_boundaries_individual()
    
    def draw_boundaries_individual(self):
        """Fallback: Draw boundaries as individual segments"""
        # Draw ARTCC HIGH boundaries
        if self.artcc_high_var.get():
            for boundary_idx, boundary in enumerate(self.artcc_high_boundaries):
                segments = boundary.get('segments', [])
                for segment_idx, segment in enumerate(segments):
                    start = segment.get('start')
                    end = segment.get('end')
                    if start and end:
                        try:
                            path = self.map_widget.set_path(
                                [start, end],
                                color='#ff0000',
                                width=2,
                                name=f"ARTCC_HIGH_{boundary_idx}_{segment_idx}"
                            )
                            if path:
                                self.drawn_paths.append(path)
                        except Exception:
                            pass
        
        # Draw ARTCC LOW boundaries
        if self.artcc_low_var.get():
            for boundary_idx, boundary in enumerate(self.artcc_low_boundaries):
                segments = boundary.get('segments', [])
                for segment_idx, segment in enumerate(segments):
                    start = segment.get('start')
                    end = segment.get('end')
                    if start and end:
                        try:
                            path = self.map_widget.set_path(
                                [start, end],
                                color='#00aa00',
                                width=1,
                                name=f"ARTCC_LOW_{boundary_idx}_{segment_idx}"
                            )
                            if path:
                                self.drawn_paths.append(path)
                        except Exception:
                            pass
    
    def draw_airports(self):
        """Draw airports"""
        for point in self.airport_points:
            try:
                marker = self.map_widget.set_marker(
                    point['lat'], point['lon'],
                    text=point['name'][:10],
                    marker_color_outside='#0088ff',
                    marker_color_circle='white',
                    text_color='black',
                    font=('Arial', 8, 'bold')
                )
                if marker:
                    self.drawn_markers.append(marker)
            except Exception:
                pass
    
    def draw_fixes(self):
        """Draw fixes as BLACK X only (no name)"""
        # OPTIMIZATION: Draw fixes in batches
        fix_paths = []
        offset = 0.001
        
        for point in self.fix_points:
            # First diagonal
            fix_paths.append([
                (point['lat'] - offset, point['lon'] - offset),
                (point['lat'] + offset, point['lon'] + offset)
            ])
            # Second diagonal
            fix_paths.append([
                (point['lat'] - offset, point['lon'] + offset),
                (point['lat'] + offset, point['lon'] - offset)
            ])
        
        # Draw all fix X's at once
        for path_coords in fix_paths:
            try:
                path = self.map_widget.set_path(path_coords, color='black', width=1)
                if path:
                    self.drawn_paths.append(path)
            except Exception:
                pass
    
    def draw_vors(self):
        """Draw VOR as magenta triangle with name above"""
        for point in self.vor_points:
            try:
                offset = 0.0015
                # Draw triangle
                path1 = self.map_widget.set_path([
                    (point['lat'], point['lon'] + offset),
                    (point['lat'] - offset, point['lon'] - offset),
                    (point['lat'] + offset, point['lon'] - offset),
                    (point['lat'], point['lon'] + offset)
                ], color='#ff00ff', width=2)
                if path1:
                    self.drawn_paths.append(path1)
                
                # Add name above
                marker = self.map_widget.set_marker(
                    point['lat'] - offset - 0.001, point['lon'],
                    text=point['name'],
                    text_color='#ff00ff',
                    font=('Arial', 8, 'bold'),
                    marker_color_circle='white',
                    marker_color_outside='white'
                )
                if marker:
                    self.drawn_markers.append(marker)
            except Exception:
                pass
    
    def draw_ndbs(self):
        """Draw NDB as yellow square with name above"""
        for point in self.ndb_points:
            try:
                offset = 0.001
                # Draw square
                path1 = self.map_widget.set_path([
                    (point['lat'] - offset, point['lon'] - offset),
                    (point['lat'] - offset, point['lon'] + offset),
                    (point['lat'] + offset, point['lon'] + offset),
                    (point['lat'] + offset, point['lon'] - offset),
                    (point['lat'] - offset, point['lon'] - offset)
                ], color='#ffaa00', width=2)
                if path1:
                    self.drawn_paths.append(path1)
                
                # Add name above
                marker = self.map_widget.set_marker(
                    point['lat'] - offset - 0.001, point['lon'],
                    text=point['name'],
                    text_color='#ffaa00',
                    font=('Arial', 8, 'bold'),
                    marker_color_circle='white',
                    marker_color_outside='white'
                )
                if marker:
                    self.drawn_markers.append(marker)
            except Exception:
                pass
    
    def clear_all_drawn_items(self):
        """Clear all drawn paths and markers"""
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
    
    def show_all(self):
        """Show all data"""
        self.artcc_high_var.set(True)
        self.artcc_low_var.set(True)
        self.airports_var.set(True)
        self.fixes_var.set(True)
        self.vor_var.set(True)
        self.ndb_var.set(True)
        self.redraw_all()
    
    def hide_all(self):
        """Hide all data"""
        self.artcc_high_var.set(False)
        self.artcc_low_var.set(False)
        self.airports_var.set(False)
        self.fixes_var.set(False)
        self.vor_var.set(False)
        self.ndb_var.set(False)
        self.redraw_all()