"""
Map Viewer Module
Displays positions and SCT data on an interactive folium map
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
import os
import tempfile
import folium
from folium import plugins
from folium.features import DivIcon
import re
from PIL import Image, ImageTk
import io

class MapViewer:
    def __init__(self, parent, ese_parser, sct_parser=None):
        self.parent = parent
        self.ese_parser = ese_parser
        self.sct_parser = sct_parser
        self.positions = ese_parser.get_positions()
        
        # Get SCT data if available
        self.sct_data = sct_parser.get_data() if sct_parser else {}
        self.airspace_classes = sct_parser.get_airspace_classes() if sct_parser else {}
        
        # Map file path
        self.map_file = None
        
        # Visibility toggles
        self.show_controllers = tk.BooleanVar(value=True)
        self.show_airports = tk.BooleanVar(value=True)
        self.show_vors = tk.BooleanVar(value=True)
        self.show_ndbs = tk.BooleanVar(value=True)
        self.show_fixes = tk.BooleanVar(value=True)
        self.show_airways = tk.BooleanVar(value=True)
        
        # Airspace class toggles
        self.show_class_a = tk.BooleanVar(value=True)
        self.show_class_b = tk.BooleanVar(value=True)
        self.show_class_c = tk.BooleanVar(value=True)
        self.show_class_d = tk.BooleanVar(value=True)
        self.show_class_e = tk.BooleanVar(value=True)
        self.show_class_f = tk.BooleanVar(value=False)
        self.show_class_g = tk.BooleanVar(value=False)
        self.show_other = tk.BooleanVar(value=True)
        
        # Setup UI
        self.setup_ui()
        
        # Create initial map
        self.create_map()
    
    def setup_ui(self):
        self.map_frame = tk.Frame(self.parent, bg='white')
        self.map_frame.pack(fill='both', expand=True)
        
        # Control panel
        control_frame = tk.Frame(self.map_frame, bg='#f5f5f5', height=120)
        control_frame.pack(fill='x', pady=(0, 5))
        control_frame.pack_propagate(False)
        
        # Create notebook for organized controls
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Data Layers tab
        layers_tab = tk.Frame(notebook, bg='white')
        notebook.add(layers_tab, text="Data Layers")
        
        # Airspace Classes tab
        airspace_tab = tk.Frame(notebook, bg='white')
        notebook.add(airspace_tab, text="Airspace Classes")
        
        # Populate Data Layers tab
        self.create_layers_controls(layers_tab)
        
        # Populate Airspace Classes tab
        self.create_airspace_controls(airspace_tab)
        
        # Map display area
        self.map_display_frame = tk.Frame(self.map_frame, bg='white')
        self.map_display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Map status label
        self.status_label = tk.Label(
            self.map_display_frame,
            text="Loading map...",
            font=('Arial', 10),
            bg='white',
            fg='#666666'
        )
        self.status_label.pack(pady=20)
    
    def create_layers_controls(self, parent):
        """Create controls for data layers"""
        # Controllers
        tk.Checkbutton(
            parent, text="Controllers", variable=self.show_controllers,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="●", fg='red', bg='white', font=('Arial', 12)).grid(row=0, column=1, sticky='w')
        
        # Airports
        tk.Checkbutton(
            parent, text="Airports", variable=self.show_airports,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="✈", fg='blue', bg='white', font=('Arial', 12)).grid(row=0, column=3, sticky='w')
        
        # VORs
        tk.Checkbutton(
            parent, text="VORs", variable=self.show_vors,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="◇", fg='purple', bg='white', font=('Arial', 12)).grid(row=1, column=1, sticky='w')
        
        # NDBs
        tk.Checkbutton(
            parent, text="NDBs", variable=self.show_ndbs,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="△", fg='orange', bg='white', font=('Arial', 12)).grid(row=1, column=3, sticky='w')
        
        # Fixes
        tk.Checkbutton(
            parent, text="Fixes", variable=self.show_fixes,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="+", fg='green', bg='white', font=('Arial', 12)).grid(row=2, column=1, sticky='w')
        
        # Airways
        tk.Checkbutton(
            parent, text="Airways", variable=self.show_airways,
            bg='white', font=('Arial', 9), command=self.update_map
        ).grid(row=2, column=2, sticky='w', padx=10, pady=5)
        
        tk.Label(parent, text="━", fg='cyan', bg='white', font=('Arial', 12)).grid(row=2, column=3, sticky='w')
        
        # Action buttons
        button_frame = tk.Frame(parent, bg='white')
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        tk.Button(
            button_frame, text="Refresh Map", command=self.update_map,
            bg='#3498db', fg='white', font=('Arial', 9), padx=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame, text="Open in Browser", command=self.open_in_browser,
            bg='#2ecc71', fg='white', font=('Arial', 9), padx=15
        ).pack(side='left', padx=5)
        
        # Status label
        self.map_status = tk.Label(
            button_frame,
            text="",
            font=('Arial', 9),
            bg='white',
            fg='#666666'
        )
        self.map_status.pack(side='left', padx=20)
    
    def create_airspace_controls(self, parent):
        """Create controls for airspace classes"""
        class_colors = {
            'A': '#FF0000',  # Red
            'B': '#FF6600',  # Orange
            'C': '#FFFF00',  # Yellow
            'D': '#00FF00',  # Green
            'E': '#0000FF',  # Blue
            'F': '#6600FF',  # Purple
            'G': '#FF00FF',  # Magenta
            'OTHER': '#888888'  # Gray
        }
        
        class_vars = {
            'A': self.show_class_a,
            'B': self.show_class_b,
            'C': self.show_class_c,
            'D': self.show_class_d,
            'E': self.show_class_e,
            'F': self.show_class_f,
            'G': self.show_class_g,
            'OTHER': self.show_other
        }
        
        row = 0
        col = 0
        
        for cls, var in class_vars.items():
            color_label = tk.Label(parent, text="■", fg=class_colors[cls], bg='white', font=('Arial', 14))
            color_label.grid(row=row, column=col*2, sticky='w', padx=(10, 2), pady=5)
            
            text = f"Class {cls}" if cls != 'OTHER' else "Other Airspace"
            tk.Checkbutton(
                parent, text=text, variable=var,
                bg='white', font=('Arial', 9), command=self.update_map
            ).grid(row=row, column=col*2+1, sticky='w', padx=(0, 20), pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Add info label
        info_label = tk.Label(
            parent,
            text="Note: Airspace visibility requires SCT file",
            font=('Arial', 8, 'italic'),
            bg='white',
            fg='#666666'
        )
        info_label.grid(row=row+1, column=0, columnspan=8, pady=(10, 0))
    
    def create_map(self):
        """Create the folium map"""
        # Get all coordinates for centering
        all_coords = []
        
        # Add controller positions
        for position in self.positions:
            coords = self.extract_coordinates(position)
            if coords:
                all_coords.append(coords)
        
        # Add SCT airports if available
        if self.sct_data.get('airports'):
            for airport in self.sct_data['airports']:
                all_coords.append((airport['lat'], airport['lon']))
        
        if not all_coords:
            self.status_label.config(text="No coordinate data available")
            return
        
        # Calculate center
        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
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
        if self.sct_parser:
            self.add_airspace()
            self.add_airways()
        
        self.add_controllers()
        self.add_airports()
        self.add_vors()
        self.add_ndbs()
        self.add_fixes()
        
        # Add controls
        folium.LayerControl().add_to(self.m)
        plugins.Fullscreen().add_to(self.m)
        plugins.MiniMap().add_to(self.m)
        
        # Add legend
        self.add_legend()
        
        # Save and display map
        self.save_and_display_map()
    
    def add_airspace(self):
        """Add airspace classes to map"""
        if not self.sct_data.get('airspace'):
            return
        
        class_colors = {
            'A': 'red',
            'B': 'orange',
            'C': 'yellow',
            'D': 'green',
            'E': 'blue',
            'F': 'purple',
            'G': 'magenta',
            'UNKNOWN': 'gray',
            'OTHER': 'gray'
        }
        
        class_opacity = {
            'A': 0.3,
            'B': 0.25,
            'C': 0.2,
            'D': 0.15,
            'E': 0.1,
            'F': 0.1,
            'G': 0.1,
            'UNKNOWN': 0.1,
            'OTHER': 0.1
        }
        
        for airspace in self.sct_data['airspace']:
            cls = airspace.get('class', 'UNKNOWN')
            
            # Check if this class should be shown
            if not self.should_show_airspace_class(cls):
                continue
            
            coordinates = airspace.get('coordinates', [])
            if len(coordinates) >= 3:
                # Convert coordinates to list of tuples
                coords = [(c['lat'], c['lon']) for c in coordinates]
                
                # Create popup text
                popup_text = f"""
                <b>{airspace.get('name', 'Airspace')}</b><br>
                Type: {airspace.get('type', 'Unknown')}<br>
                Class: {cls}<br>
                Floor: {airspace.get('floor', 'GND')}<br>
                Ceiling: {airspace.get('ceiling', 'UNL')}
                """
                
                # Add polygon to map
                folium.Polygon(
                    locations=coords,
                    popup=folium.Popup(popup_text, max_width=300),
                    color=class_colors.get(cls, 'gray'),
                    fill=True,
                    fill_color=class_colors.get(cls, 'gray'),
                    fill_opacity=class_opacity.get(cls, 0.1),
                    weight=2,
                    opacity=0.7,
                    tooltip=airspace.get('name', f"Class {cls} Airspace")
                ).add_to(self.m)
    
    def should_show_airspace_class(self, cls):
        """Check if airspace class should be shown"""
        cls = cls.upper()
        
        if cls == 'A':
            return self.show_class_a.get()
        elif cls == 'B':
            return self.show_class_b.get()
        elif cls == 'C':
            return self.show_class_c.get()
        elif cls == 'D':
            return self.show_class_d.get()
        elif cls == 'E':
            return self.show_class_e.get()
        elif cls == 'F':
            return self.show_class_f.get()
        elif cls == 'G':
            return self.show_class_g.get()
        else:
            return self.show_other.get()
    
    def add_airways(self):
        """Add airways to map"""
        if not self.show_airways.get():
            return
        
        # Add high airways
        if 'high_airways' in self.sct_data:
            for airway in self.sct_data['high_airways']:
                for segment in airway.get('segments', []):
                    if len(segment) >= 2:
                        points = [(p['lat'], p['lon']) for p in segment]
                        folium.PolyLine(
                            points,
                            color='cyan',
                            weight=2,
                            opacity=0.7,
                            popup=f"High Airway: {airway.get('name', '')}",
                            tooltip="High Airway"
                        ).add_to(self.m)
        
        # Add low airways
        if 'low_airways' in self.sct_data:
            for airway in self.sct_data['low_airways']:
                for segment in airway.get('segments', []):
                    if len(segment) >= 2:
                        points = [(p['lat'], p['lon']) for p in segment]
                        folium.PolyLine(
                            points,
                            color='lightblue',
                            weight=1,
                            opacity=0.5,
                            popup=f"Low Airway: {airway.get('name', '')}",
                            tooltip="Low Airway"
                        ).add_to(self.m)
    
    def add_controllers(self):
        """Add controller positions to map"""
        if not self.show_controllers.get():
            return
        
        for position in self.positions:
            coords = self.extract_coordinates(position)
            if coords:
                lat, lon = coords
                
                # Get color based on position type
                color = self.get_position_color(position['type'])
                
                # Create popup text
                popup_text = f"""
                <b>{position['callsign']}</b><br>
                Name: {position['name']}<br>
                Type: {position['type']}<br>
                Frequency: {position['frequency']}<br>
                ID: {position['identifier']}<br>
                Lat: {lat:.4f}° Lon: {lon:.4f}°
                """
                
                # Add marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=300),
                    color='white',
                    fill=True,
                    fill_color=color,
                    fill_opacity=1.0,
                    weight=2,
                    tooltip=position['callsign']
                ).add_to(self.m)
                
                # Add label
                folium.map.Marker(
                    [lat, lon],
                    icon=DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(0, 0),
                        html=f'<div style="font-size: 9pt; color: white; background-color: {color}; padding: 2px 5px; border-radius: 3px; font-weight: bold;">{position["callsign"]}</div>'
                    )
                ).add_to(self.m)
    
    def add_airports(self):
        """Add airports to map"""
        if not self.show_airports.get() or not self.sct_data.get('airports'):
            return
        
        for airport in self.sct_data['airports']:
            # Create popup text
            popup_text = f"""
            <b>✈ {airport['icao']}</b><br>
            {airport.get('name', airport['icao'])}<br>
            Lat: {airport['lat']:.4f}°<br>
            Lon: {airport['lon']:.4f}°
            """
            if 'elevation' in airport:
                popup_text += f"<br>Elevation: {airport['elevation']} ft"
            
            # Add marker
            folium.Marker(
                location=[airport['lat'], airport['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='blue', icon='plane', prefix='fa'),
                tooltip=f"Airport: {airport['icao']}"
            ).add_to(self.m)
    
    def add_vors(self):
        """Add VOR stations to map"""
        if not self.show_vors.get() or not self.sct_data.get('vor'):
            return
        
        for vor in self.sct_data['vor']:
            # Create popup text
            popup_text = f"""
            <b>◇ {vor['identifier']}</b><br>
            {vor.get('name', vor['identifier'])}<br>
            Type: VOR<br>
            Frequency: {vor.get('frequency', 'N/A')}<br>
            Lat: {vor['lat']:.4f}°<br>
            Lon: {vor['lon']:.4f}°
            """
            
            # Add marker
            folium.Marker(
                location=[vor['lat'], vor['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='purple', icon='circle', prefix='fa'),
                tooltip=f"VOR: {vor['identifier']}"
            ).add_to(self.m)
    
    def add_ndbs(self):
        """Add NDB stations to map"""
        if not self.show_ndbs.get() or not self.sct_data.get('ndb'):
            return
        
        for ndb in self.sct_data['ndb']:
            # Create popup text
            popup_text = f"""
            <b>△ {ndb['identifier']}</b><br>
            {ndb.get('name', ndb['identifier'])}<br>
            Type: NDB<br>
            Frequency: {ndb.get('frequency', 'N/A')}<br>
            Lat: {ndb['lat']:.4f}°<br>
            Lon: {ndb['lon']:.4f}°
            """
            
            # Add marker
            folium.Marker(
                location=[ndb['lat'], ndb['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='orange', icon='triangle', prefix='fa'),
                tooltip=f"NDB: {ndb['identifier']}"
            ).add_to(self.m)
    
    def add_fixes(self):
        """Add fixes to map"""
        if not self.show_fixes.get() or not self.sct_data.get('fixes'):
            return
        
        # Limit to first 200 fixes to avoid overcrowding
        for fix in self.sct_data['fixes'][:200]:
            # Create popup text
            popup_text = f"""
            <b>+ {fix['identifier']}</b><br>
            {fix.get('name', fix['identifier'])}<br>
            Type: FIX<br>
            Lat: {fix['lat']:.4f}°<br>
            Lon: {fix['lon']:.4f}°
            """
            
            # Add marker
            folium.CircleMarker(
                location=[fix['lat'], fix['lon']],
                radius=3,
                popup=folium.Popup(popup_text, max_width=300),
                color='green',
                fill=True,
                fill_color='green',
                fill_opacity=1.0,
                weight=1,
                tooltip=f"Fix: {fix['identifier']}"
            ).add_to(self.m)
    
    def add_legend(self):
        """Add a legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 280px; height: auto;
                    border: 2px solid grey; z-index: 9999; font-size: 12px;
                    background-color: white;
                    opacity: 0.95;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <b style="font-size: 14px;">Map Legend</b><br>
        <hr style="margin: 5px 0;">
        
        <b>Airspace Classes:</b><br>
        <i class="fa fa-square" style="color:red"></i> Class A<br>
        <i class="fa fa-square" style="color:orange"></i> Class B<br>
        <i class="fa fa-square" style="color:yellow"></i> Class C<br>
        <i class="fa fa-square" style="color:green"></i> Class D<br>
        <i class="fa fa-square" style="color:blue"></i> Class E<br>
        <i class="fa fa-square" style="color:purple"></i> Class F/G<br>
        
        <b>Controllers:</b><br>
        <i class="fa fa-circle" style="color:red"></i> Tower/Ground<br>
        <i class="fa fa-circle" style="color:orange"></i> Approach/Departure<br>
        <i class="fa fa-circle" style="color:green"></i> Center<br>
        <i class="fa fa-circle" style="color:yellow"></i> ATIS/DEL/FSS<br>
        
        <b>Navigation:</b><br>
        <i class="fa fa-plane" style="color:blue"></i> Airport<br>
        <i class="fa fa-diamond" style="color:purple"></i> VOR<br>
        <i class="fa fa-caret-up" style="color:orange"></i> NDB<br>
        <i class="fa fa-plus" style="color:green"></i> Fix<br>
        <i class="fa fa-minus" style="color:cyan"></i> Airways<br>
        
        <div style="font-size: 10px; color: #666; margin-top: 5px;">
        Click markers for details • Drag to pan • Scroll to zoom
        </div>
        </div>
        '''
        
        self.m.get_root().html.add_child(folium.Element(legend_html))
    
    def save_and_display_map(self):
        """Save the map and display it"""
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        self.map_file = os.path.join(temp_dir, f"ese_viewer_map_{os.getpid()}.html")
        
        try:
            self.m.save(self.map_file)
            self.status_label.config(text=f"Map saved to: {self.map_file}")
            
            # Update status in control panel
            if hasattr(self, 'map_status'):
                self.map_status.config(text=f"✓ Map ready")
            
            # Try to embed map using tkinterweb
            self.display_embedded_map()
            
        except Exception as e:
            self.status_label.config(text=f"Error saving map: {str(e)}")
    
    def display_embedded_map(self):
        """Try to display the map embedded in the application"""
        try:
            # Clear the display frame
            for widget in self.map_display_frame.winfo_children():
                widget.destroy()
            
            # Try to use tkinterweb
            try:
                import tkinterweb
                
                # Create browser frame
                browser_frame = tkinterweb.HtmlFrame(self.map_display_frame)
                browser_frame.load_file(self.map_file)
                browser_frame.pack(fill='both', expand=True)
                
                # Add a small status bar at the bottom
                status_bar = tk.Frame(self.map_display_frame, bg='#f0f0f0', height=25)
                status_bar.pack(fill='x', side='bottom')
                status_bar.pack_propagate(False)
                
                tk.Label(
                    status_bar,
                    text=f"Interactive map loaded | File: {os.path.basename(self.map_file)}",
                    font=('Arial', 8),
                    bg='#f0f0f0',
                    fg='#666666'
                ).pack(side='left', padx=10)
                
                tk.Button(
                    status_bar,
                    text="Reload",
                    font=('Arial', 8),
                    command=self.update_map,
                    padx=10
                ).pack(side='right', padx=5)
                
                tk.Button(
                    status_bar,
                    text="Open Full",
                    font=('Arial', 8),
                    command=self.open_in_browser,
                    padx=10
                ).pack(side='right', padx=5)
                
            except ImportError:
                # tkinterweb not available, show alternative
                self.show_map_alternative()
                
        except Exception as e:
            self.show_map_alternative()
    
    def show_map_alternative(self):
        """Show alternative when embedded map isn't available"""
        for widget in self.map_display_frame.winfo_children():
            widget.destroy()
        
        # Show message with option to open in browser
        message_frame = tk.Frame(self.map_display_frame, bg='white')
        message_frame.pack(fill='both', expand=True)
        
        tk.Label(
            message_frame,
            text="Interactive Map Created",
            font=('Arial', 16, 'bold'),
            bg='white'
        ).pack(pady=20)
        
        tk.Label(
            message_frame,
            text="The map has been saved as an HTML file.",
            font=('Arial', 11),
            bg='white'
        ).pack(pady=5)
        
        tk.Label(
            message_frame,
            text=f"Location: {self.map_file}",
            font=('Arial', 10),
            bg='white',
            fg='#666666'
        ).pack(pady=5)
        
        # Action buttons
        button_frame = tk.Frame(message_frame, bg='white')
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="Open in Web Browser",
            font=('Arial', 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            command=self.open_in_browser
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="Refresh Map",
            font=('Arial', 11),
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=10,
            command=self.update_map
        ).pack(side='left', padx=10)
        
        # Installation hint
        install_frame = tk.Frame(message_frame, bg='#f8f9fa', padx=20, pady=10)
        install_frame.pack(pady=20)
        
        tk.Label(
            install_frame,
            text="Tip: For embedded map display, install tkinterweb:",
            font=('Arial', 9),
            bg='#f8f9fa'
        ).pack()
        
        tk.Label(
            install_frame,
            text="pip install tkinterweb",
            font=('Courier', 9, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        ).pack(pady=5)
    
    def update_map(self):
        """Update the map with current settings"""
        self.status_label.config(text="Updating map...")
        self.create_map()
    
    def open_in_browser(self):
        """Open the map in the default web browser"""
        if self.map_file and os.path.exists(self.map_file):
            webbrowser.open(f'file://{self.map_file}')
        else:
            # Create map first
            self.status_label.config(text="Creating map for browser...")
            self.create_map()
            if self.map_file and os.path.exists(self.map_file):
                webbrowser.open(f'file://{self.map_file}')
    
    def get_position_color(self, pos_type):
        """Get color for position type"""
        pos_type = pos_type.upper() if pos_type else ''
        
        if pos_type in ['TWR', 'GND']:
            return 'red'
        elif pos_type in ['APP', 'DEP']:
            return 'orange'
        elif pos_type == 'CTR':
            return 'green'
        elif pos_type in ['ATIS', 'DEL', 'FSS']:
            return 'yellow'
        else:
            return 'gray'
    
    def extract_coordinates(self, position):
        """Extract coordinates from position data"""
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
        """Parse coordinate string to decimal degrees"""
        if not coord_str:
            return None
        
        coord_str = coord_str.strip().upper()
        
        # Parse N/S coordinate (latitude)
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
        
        # Parse E/W coordinate (longitude)
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