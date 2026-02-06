import random
import requests
from datetime import datetime
import json
from tkinter import messagebox

class RandomScenarioGenerator:
    def __init__(self, creator):
        self.creator = creator
        
        # Real airline callsigns with their typical routes
        self.airlines = {
            'SAA': {'name': 'South African Airways', 'routes': ['FAOR-FACT', 'FAOR-FALE', 'FAOR-FAGG', 'FAOR-FAPE']},
            'BAW': {'name': 'British Airways', 'routes': ['FAOR-EGLL', 'FACT-EGLL']},
            'UAL': {'name': 'United Airlines', 'routes': ['FAOR-KEWR', 'FAOR-KIAD']},
            'DLH': {'name': 'Lufthansa', 'routes': ['FAOR-EDDF', 'FACT-EDDF']},
            'AFR': {'name': 'Air France', 'routes': ['FAOR-LFPG', 'FACT-LFPG']},
            'KLM': {'name': 'KLM Royal Dutch Airlines', 'routes': ['FAOR-EHAM', 'FACT-EHAM']},
            'VIR': {'name': 'Virgin Atlantic', 'routes': ['FAOR-EGLL']},
            'QTR': {'name': 'Qatar Airways', 'routes': ['FAOR-OTBD']},
            'UAE': {'name': 'Emirates', 'routes': ['FAOR-OMDB']},
            'THY': {'name': 'Turkish Airlines', 'routes': ['FAOR-LTBA']},
            'SIA': {'name': 'Singapore Airlines', 'routes': ['FAOR-WSSS']},
            'ANA': {'name': 'All Nippon Airways', 'routes': ['FAOR-RJTT']},
            'AAL': {'name': 'American Airlines', 'routes': ['FAOR-KJFK']},
            'DAL': {'name': 'Delta Air Lines', 'routes': ['FAOR-KATL']},
            'EZY': {'name': 'EasyJet', 'routes': ['FAOR-EGSS']},
            'RYR': {'name': 'Ryanair', 'routes': ['FACT-EIDW']}
        }
        
        # Aircraft types by size/category
        self.aircraft_types = {
            'small': ['E190', 'E195', 'CRJ9', 'CRJ7', 'DH8D', 'AT76'],
            'medium': ['A320', 'A321', 'A319', 'B738', 'B739', 'B737', 'A220'],
            'large': ['A333', 'A332', 'B789', 'B788', 'A359', 'A350', 'B77W', 'B77L'],
            'heavy': ['A388', 'B748', 'B77W', 'B77L', 'B744']
        }
        
        # Common fixes in South African airspace
        self.south_africa_fixes = [
            'AVAGO', 'NIBEX', 'OKPIT', 'UNPOM', 'VEKOP', 'ETLIG',
            'RAGUL', 'APDAK', 'EXOBI', 'NESAN', 'EVIPI', 'ETMIT',
            'OR370', 'OR371', 'OR372', 'OR373', 'OR391', 'OR392',
            'OR393', 'OR394', 'OR395', 'OR396', 'OR377'
        ]
        
        # Position coordinates around major airports
        self.positions = {
            'FAOR': {'lat': -26.145, 'lon': 28.234},
            'FACT': {'lat': -33.964, 'lon': 18.601},
            'FALE': {'lat': -29.614, 'lon': 30.399},
            'FAGG': {'lat': -34.005, 'lon': 22.378},
            'FAPE': {'lat': -33.984, 'lon': 25.617},
            'FAEL': {'lat': -33.035, 'lon': 27.825}
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
        """Generate random controller positions"""
        controller_types = ['TWR', 'GND', 'APP', 'DEP', 'CTR', 'DEL', 'ATIS']
        airports = ['FAOR', 'FACT', 'FALE', 'FAGG', 'FAPE', 'FAEL']
        
        # Clear existing controllers
        for item in self.creator.controller_tree.get_children():
            self.creator.controller_tree.delete(item)
        
        # Generate center controllers
        center_controllers = [
            ('FAJA_CTR', '134.400', 'CTR'),
            ('FAJA_NW_CTR', '126.700', 'CTR'),
            ('FAJA_SW_CTR', '128.300', 'CTR'),
            ('FAJA_SE_CTR', '132.150', 'CTR')
        ]
        
        for callsign, freq, ctype in center_controllers:
            self.creator.controller_tree.insert('', 'end', values=(
                callsign, freq, ctype, '✓'
            ))
        
        # Generate airport-specific controllers
        for airport in airports[:3]:  # Only first 3 airports
            # Tower
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_TWR", "118.100", 'TWR', '✓'
            ))
            # Ground
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_GND", "121.900", 'GND', '✓'
            ))
            # Approach/Departure
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_APP", "124.500", 'APP', '✓'
            ))
            # Delivery
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_DEL", "121.700", 'DEL', '✓'
            ))
            # ATIS
            self.creator.controller_tree.insert('', 'end', values=(
                f"{airport}_ATIS", "126.200", 'ATIS', '✓'
            ))
    
    def generate_random_aircraft(self, index):
        """Generate random aircraft with realistic data"""
        # Select random airline
        airline_code = random.choice(list(self.airlines.keys()))
        
        # Generate flight number
        if airline_code in ['SAA', 'BAW', 'UAL']:
            flight_num = random.randint(1, 999)
        else:
            flight_num = random.randint(100, 9999)
        
        callsign = f"{airline_code}{flight_num}"
        
        # Select aircraft type based on airline and route
        if airline_code in ['UAE', 'SIA', 'QTR']:
            ac_type = random.choice(self.aircraft_types['heavy'] + self.aircraft_types['large'])
        elif airline_code in ['EZY', 'RYR']:
            ac_type = random.choice(self.aircraft_types['small'] + self.aircraft_types['medium'])
        else:
            ac_type = random.choice(self.aircraft_types['medium'] + self.aircraft_types['large'])
        
        # Generate position
        airport = random.choice(list(self.positions.keys()))
        base_pos = self.positions[airport]
        
        # Add random offset for variety
        lat = base_pos['lat'] + random.uniform(-2.0, 2.0)
        lon = base_pos['lon'] + random.uniform(-2.0, 2.0)
        position = f"{lat:.6f}, {lon:.6f}"
        
        # Generate altitude based on aircraft type and position
        if 'heavy' in ac_type or 'large' in ac_type:
            altitude = random.choice([28000, 32000, 35000, 38000])
        else:
            altitude = random.choice([5000, 8000, 10000, 12000, 15000, 18000])
        
        # Generate route
        num_fixes = random.randint(3, 8)
        route_fixes = random.sample(self.south_africa_fixes, min(num_fixes, len(self.south_africa_fixes)))
        route = ' '.join(route_fixes)
        
        # Add altitude restrictions
        if random.random() > 0.5:
            fix_idx = random.randint(0, len(route_fixes)-2)
            alt_restriction = random.choice([8000, 10000, 13000, 16000])
            route = route.replace(route_fixes[fix_idx], f"{route_fixes[fix_idx]}/{alt_restriction}")
        
        # Add approach if near destination
        if random.random() > 0.7:
            runway = random.choice(['03R', '03L', '21R', '21L'])
            route += f" ILS{runway}"
        
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
    
    def generate_aircraft_at_entry_fixes(self, entry_fixes, airport_icao):
        """Generate aircraft at entry fixes"""
        if not entry_fixes:
            return []
        
        aircraft_list = []
        
        # Generate 3-8 aircraft at random entry fixes
        num_aircraft = random.randint(3, min(8, len(entry_fixes)))
        selected_fixes = random.sample(entry_fixes, num_aircraft)
        
        for i, fix in enumerate(selected_fixes):
            # Select random airline
            airline_code = random.choice(list(self.airlines.keys()))
            flight_num = random.randint(100, 999)
            callsign = f"{airline_code}{flight_num}"
            
            # Select aircraft type
            ac_type = random.choice(self.aircraft_types['medium'] + self.aircraft_types['large'])
            
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
            
            # Generate route
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
        # Different route patterns based on airport
        if airport_icao == 'FAOR':
            patterns = [
                f"{fix_name} VEKOP/13000 JS2T1/13000 JS2F1/8000 ILS03R",
                f"{fix_name} ETLIG JS2T1/13000 JS2F1/8000 ILS03L",
                f"{fix_name} OR377 VEKOP/13000 JS2T1/13000 JS2F1/8000 ILS21R",
                f"{fix_name} OR391 OR392 ETLIG JS2T1/13000 JS2F1/8000 ILS21L",
                f"{fix_name} AVAGO OR370 OR371 OR372 OR373"
            ]
        elif airport_icao == 'FACT':
            patterns = [
                f"{fix_name} DCT FACT",
                f"{fix_name} NIBEX DCT FACT",
                f"{fix_name} OR377 DCT FACT"
            ]
        elif airport_icao == 'FALE':
            patterns = [
                f"{fix_name} DCT FALE",
                f"{fix_name} UNPOM DCT FALE",
                f"{fix_name} OR391 OR392 DCT FALE"
            ]
        else:
            # Generic route
            patterns = [
                f"{fix_name} DCT {airport_icao}",
                f"{fix_name} VOR1 VOR2 {airport_icao}"
            ]
        
        return random.choice(patterns)
    
    def get_real_flight_plan(self, departure, arrival):
        """Try to get real flight plan from online source (placeholder)"""
        # This would connect to a flight planning API in a real implementation
        # For now, return a simulated flight plan
        
        # Example route structures
        route_templates = [
            f"{departure} DCT {random.choice(self.south_africa_fixes)} DCT {arrival}",
            f"{departure} {random.choice(self.south_africa_fixes)} {random.choice(self.south_africa_fixes)} {arrival}",
            f"{departure} VOR1 VOR2 {random.choice(self.south_africa_fixes)} {arrival}"
        ]
        
        return random.choice(route_templates)