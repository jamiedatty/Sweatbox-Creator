import random
import re
from datetime import datetime
from tkinter import messagebox

class RandomScenarioGenerator:
    def __init__(self, creator):
        self.creator = creator
        
        # Aircraft types by size/category
        self.aircraft_types = {
            'small': ['E190', 'E195', 'CRJ9', 'CRJ7', 'DH8D', 'AT76'],
            'medium': ['A320', 'A321', 'A319', 'B738', 'B739', 'B737', 'A220'],
            'large': ['A333', 'A332', 'B789', 'B788', 'A359', 'A350', 'B77W', 'B77L'],
            'heavy': ['A388', 'B748', 'B77W', 'B77L', 'B744']
        }
    
    def generate_random_scenario(self):
        """Generate a complete random scenario"""
        try:
            # Generate random controllers if ESE not loaded
            if not self.creator.ese_parser:
                self.generate_random_controllers()
            
            # Generate random aircraft
            num_aircraft = random.randint(8, 20)
            for i in range(num_aircraft):
                self.generate_random_aircraft(i)
            
            # Update map
            self.creator.update_aircraft_on_map()
            
            self.creator.status_label.config(text=f"Generated random scenario with {num_aircraft} aircraft")
            messagebox.showinfo("Success", f"Generated random scenario with {num_aircraft} aircraft")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate random scenario:\n{str(e)}")
    
    def generate_random_controllers(self):
        """Generate random controller positions based on loaded airports"""
        controller_types = ['TWR', 'GND', 'APP', 'DEP', 'CTR', 'DEL', 'ATIS']
        
        # Clear existing controllers
        for item in self.creator.controller_tree.get_children():
            self.creator.controller_tree.delete(item)
        
        # Get airports from map viewer
        airports = []
        if self.creator.map_viewer and hasattr(self.creator.map_viewer, 'loaded_airports'):
            airports = self.creator.map_viewer.loaded_airports
        
        # If no airports loaded, use some defaults
        if not airports:
            airports = ['FAOR', 'FACT', 'FALE', 'FAGG', 'FAPE', 'FAEL']
        
        # Generate center controllers (first 3 characters of first airport + CTR)
        if airports:
            fir_prefix = airports[0][:3] if len(airports[0]) >= 3 else 'FAJ'
            center_controllers = [
                (f'{fir_prefix}A_CTR', '134.400', 'CTR'),
                (f'{fir_prefix}A_NW_CTR', '126.700', 'CTR'),
                (f'{fir_prefix}A_SW_CTR', '128.300', 'CTR'),
                (f'{fir_prefix}A_SE_CTR', '132.150', 'CTR')
            ]
            
            for callsign, freq, ctype in center_controllers:
                self.creator.controller_tree.insert('', 'end', values=(
                    callsign, freq, ctype, '✓'
                ))
        
        # Generate airport-specific controllers for first 3 airports
        for airport in airports[:3]:
            # Generate frequencies
            twr_freq = self.generate_frequency('TWR')
            gnd_freq = self.generate_frequency('GND')
            app_freq = self.generate_frequency('APP')
            del_freq = self.generate_frequency('DEL')
            atis_freq = self.generate_frequency('ATIS')
            
            # Tower
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_TWR", twr_freq, 'TWR', '✓'
            ))
            # Ground
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_GND", gnd_freq, 'GND', '✓'
            ))
            # Approach/Departure
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_APP", app_freq, 'APP', '✓'
            ))
            # Delivery
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_DEL", del_freq, 'DEL', '✓'
            ))
            # ATIS
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_ATIS", atis_freq, 'ATIS', '✓'
            ))
    
    def generate_frequency(self, controller_type):
        """Generate realistic frequency based on controller type"""
        if controller_type == 'TWR':
            return f"118.{random.randint(1, 9):03d}"
        elif controller_type == 'GND':
            return f"121.{random.randint(1, 9):03d}"
        elif controller_type == 'APP':
            return f"124.{random.randint(1, 9):03d}"
        elif controller_type == 'DEL':
            return f"121.{random.randint(1, 9):03d}"
        elif controller_type == 'ATIS':
            return f"126.{random.randint(1, 9):03d}"
        else:  # CTR
            return f"{random.randint(118, 136)}.{random.randint(1, 9):03d}"
    
    def generate_random_aircraft(self, index):
        """Generate random aircraft with dynamic data"""
        # Generate random airline code (3 letters)
        airline_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        
        # Generate flight number
        flight_num = random.randint(1, 9999)
        callsign = f"{airline_code}{flight_num}"
        
        # Select aircraft type
        category = random.choice(['small', 'medium', 'large', 'heavy'])
        ac_type = random.choice(self.aircraft_types[category])
        
        # Generate position based on loaded airports
        lat, lon = self.generate_random_position()
        position = f"{lat:.6f}, {lon:.6f}"
        
        # Generate altitude based on aircraft type
        if category in ['heavy', 'large']:
            altitude = random.choice([28000, 32000, 35000, 38000])
        else:
            altitude = random.choice([5000, 8000, 10000, 12000, 15000, 18000])
        
        # Generate route
        route = self.generate_random_route()
        
        # Generate speed and heading
        speed = str(random.randint(250, 480)).rjust(3)
        heading = str(random.randint(0, 359)).rjust(3)
        
        # Add to aircraft tree
        self.creator.aircraft_details_tree.insert('', 'end', values=(
            callsign,
            ac_type,
            f"{altitude}ft",
            position,
            route,
            speed,
            heading
        ))
    
    def generate_random_position(self):
        """Generate random position near loaded airports"""
        # Get airports from map viewer
        airports = []
        if self.creator.map_viewer and hasattr(self.creator.map_viewer, 'loaded_airports'):
            airports = self.creator.map_viewer.loaded_airports
        
        # If we have airports from SCT data, use those coordinates
        if self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'airports' in data and data['airports']:
                airport = random.choice(data['airports'])
                if 'latitude' in airport and 'longitude' in airport:
                    lat = airport['latitude'] + random.uniform(-2.0, 2.0)
                    lon = airport['longitude'] + random.uniform(-2.0, 2.0)
                    return lat, lon
        
        # Default fallback position
        return random.uniform(-90, 90), random.uniform(-180, 180)
    
    def generate_random_route(self):
        """Generate random route using fixes from SCT data"""
        route_parts = []
        
        # Get fixes from SCT parser if available
        fixes = []
        if self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'fixes' in data:
                fixes = [fix['name'] for fix in data['fixes'] if 'name' in fix]
        
        # If we have fixes, use them
        if fixes:
            num_fixes = random.randint(2, 6)
            selected_fixes = random.sample(fixes, min(num_fixes, len(fixes)))
            route_parts.extend(selected_fixes)
        else:
            # Generate generic route
            route_parts = ['DCT', 'VOR1', 'VOR2']
        
        # Add altitude restrictions randomly
        if random.random() > 0.5 and len(route_parts) > 1:
            fix_idx = random.randint(0, len(route_parts)-2)
            alt_restriction = random.choice([8000, 10000, 13000, 16000])
            route_parts[fix_idx] = f"{route_parts[fix_idx]}/{alt_restriction}"
        
        # Add approach randomly
        if random.random() > 0.7:
            runway = random.choice(['03R', '03L', '21R', '21L', '09', '27', '18', '36'])
            route_parts.append(f"ILS{runway}")
        
        return ' '.join(route_parts)
    
    def generate_aircraft_at_entry_fixes(self, entry_fixes, airport_icao):
        """Generate aircraft at entry fixes"""
        if not entry_fixes:
            return []
        
        aircraft_list = []
        
        # Generate 3-8 aircraft at random entry fixes
        num_aircraft = random.randint(3, min(8, len(entry_fixes)))
        selected_fixes = random.sample(entry_fixes, num_aircraft)
        
        for i, fix in enumerate(selected_fixes):
            # Generate airline code
            airline_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
            flight_num = random.randint(100, 999)
            callsign = f"{airline_code}{flight_num}"
            
            # Select aircraft type
            category = random.choice(['medium', 'large'])
            ac_type = random.choice(self.aircraft_types[category])
            
            # Position at fix with small offset
            lat = fix['lat'] + random.uniform(-0.05, 0.05)
            lon = fix['lon'] + random.uniform(-0.05, 0.05)
            position = f"{lat:.6f}, {lon:.6f}"
            
            # Altitude based on distance
            distance = fix.get('distance_nm', 50)
            if distance < 30:
                altitude = random.choice([5000, 6000, 7000])
            elif distance < 60:
                altitude = random.choice([8000, 10000, 12000])
            else:
                altitude = random.choice([14000, 16000, 18000])
            
            # Generate route to airport
            route = self.generate_route_to_airport(fix['name'], airport_icao)
            
            # Speed and heading
            speed = str(random.randint(250, 350)).rjust(3)
            heading = str(random.randint(0, 359)).rjust(3)
            
            aircraft_list.append({
                'callsign': callsign,
                'type': ac_type,
                'position': position,
                'altitude': f"{altitude}ft",
                'route': route,
                'speed': speed,
                'heading': heading
            })
        
        return aircraft_list
    
    def generate_route_to_airport(self, fix_name, airport_icao):
        """Generate route from fix to airport"""
        # Get fixes from SCT parser if available
        fixes = []
        if self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'fixes' in data:
                fixes = [fix['name'] for fix in data['fixes'] if 'name' in fix]
        
        # Create route
        route_parts = [fix_name]
        
        # Add intermediate fixes if available
        if fixes and len(fixes) > 2:
            num_intermediate = random.randint(1, 3)
            intermediate_fixes = random.sample([f for f in fixes if f != fix_name], 
                                             min(num_intermediate, len(fixes)-1))
            route_parts.extend(intermediate_fixes)
        
        # Add airport and approach
        route_parts.append(airport_icao)
        
        # Add approach type randomly
        if random.random() > 0.5:
            runway = random.choice(['03R', '03L', '21R', '21L', '09', '27', '18', '36'])
            route_parts.append(f"ILS{runway}")
        
        return ' '.join(route_parts)