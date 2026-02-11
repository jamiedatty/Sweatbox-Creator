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
    
    def prompt_for_controller_type(self):
        """Prompt user for controller type"""
        import tkinter as tk
        from tkinter import simpledialog
        
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Bring to front
        
        try:
            result = simpledialog.askstring(
                "Controller Type",
                "Select controller type:\nGND = Ground\nDEL = Delivery\nTWR = Tower\nAPP = Approach\nCTR = Center\nALL = All (16000-20000ft, 50-75NM)\n\nEnter: GND, DEL, TWR, APP, CTR, or ALL",
                parent=root
            )
        finally:
            root.destroy()
        
        if result:
            result = result.upper().strip()
            if result in ['GND', 'DEL', 'TWR', 'APP', 'CTR', 'ALL']:
                return result
            else:
                messagebox.showerror("Invalid", "Please enter GND, DEL, TWR, APP, CTR, or ALL")
                return None
        
        return None
    
    def generate_random_scenario(self, selected_airport=None):
        """Generate a complete random scenario"""
        try:
            # Prompt for controller type
            controller_type = self.prompt_for_controller_type()
            if controller_type is None:
                messagebox.showwarning("Cancelled", "Scenario generation cancelled")
                return  # User cancelled
            
            # Check if controller type is supported
            if controller_type != 'ALL':
                messagebox.showerror("Unavailable", f"Scenario generation for {controller_type} is unavailable. Please select 'ALL'.")
                return
            
            # Generate random controllers if ESE not loaded
            if not self.creator.ese_parser:
                self.generate_random_controllers()
            
            # Use selected airport if available
            if not selected_airport and self.creator.map_viewer:
                selected_airport = self.creator.map_viewer.get_selected_airport()
            
            # Generate random aircraft
            num_aircraft = random.randint(8, 20)
            for i in range(num_aircraft):
                self.generate_random_aircraft(i, selected_airport=selected_airport, controller_type=controller_type)
            
            # Update map
            self.creator.update_aircraft_on_map()
            
            self.creator.status_label.config(text=f"Generated random scenario with {num_aircraft} aircraft for {controller_type}")
            messagebox.showinfo("Success", f"Generated random scenario with {num_aircraft} aircraft for {controller_type}")
            
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
    
    def generate_random_aircraft(self, index, selected_airport=None, controller_type='ALL'):
        """Generate random aircraft with dynamic data"""
        # Validate selected airport
        if not selected_airport:
            messagebox.showerror("Error", "No airport selected. Please select an airport before generating aircraft.")
            return

        # Generate random airline code (3 letters)
        airline_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))

        # Generate flight number
        flight_num = random.randint(1, 9999)
        callsign = f"{airline_code}{flight_num}"

        # Select aircraft type
        category = random.choice(['small', 'medium', 'large', 'heavy'])
        ac_type = random.choice(self.aircraft_types[category])

        # Always generate position 50-75 miles from selected airport
        try:
            lat, lon = self.generate_position_miles_from_airport(selected_airport, min_miles=50, max_miles=75)
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to generate aircraft position: {str(e)}")
            return

        # Always use high altitude (16000-20000ft) for all aircraft
        altitude = random.choice([16000, 17000, 18000, 19000, 20000])

        position = f"{lat:.6f}, {lon:.6f}"

        # Generate route to airport (airport-based, no hardcoded fixes)
        route = self.generate_route_to_airport(selected_airport)

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
    
    def generate_random_position(self, selected_airport=None):
        """Generate random position based on selected airport (must be provided for "ALL" controller type)"""
        # REQUIRED: Must have selected airport for proper airport-based spawning
        if not selected_airport:
            # Fallback only if no airport selected: return position near equator/prime meridian
            # This should rarely happen with "ALL" controller type
            return random.uniform(-10, 10), random.uniform(-10, 10)
        
        # Find target airport coordinates
        target_lat, target_lon = None, None
        
        if self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'airports' in data and data['airports']:
                for airport in data['airports']:
                    if airport.get('icao') == selected_airport:
                        if 'latitude' in airport and 'longitude' in airport:
                            target_lat = airport['latitude']
                            target_lon = airport['longitude']
                            break
        
        # If airport not found in SCT, raise error
        if target_lat is None or target_lon is None:
            raise ValueError(f"Airport {selected_airport} not found in loaded SCT data. Please load SCT file with airport data.")
        
        # Generate position WITHIN 50NM of target airport (for general positioning)
        # 50 NM ≈ 0.75 degrees (at equator, varies by latitude)
        lat = target_lat + random.uniform(-0.75, 0.75)
        lon = target_lon + random.uniform(-0.75, 0.75)
        return lat, lon
    
    def generate_position_miles_from_airport(self, selected_airport=None, min_miles=50, max_miles=75):
        """Generate random position between min_miles and max_miles from airport"""
        import math

        # Find target airport coordinates
        target_lat, target_lon = None, None

        if selected_airport and self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'airports' in data and data['airports']:
                for airport in data['airports']:
                    if airport.get('icao', '').upper() == selected_airport.upper():
                        if 'latitude' in airport and 'longitude' in airport:
                            target_lat = airport['latitude']
                            target_lon = airport['longitude']
                            break

        # If airport not found in SCT, try airport_fetcher as fallback
        if target_lat is None or target_lon is None:
            try:
                from modules.parsers.airport_fetcher import fetch_airport_coordinates
                coords = fetch_airport_coordinates(selected_airport)
                if coords:
                    target_lat = coords['latitude']
                    target_lon = coords['longitude']
                    print(f"DEBUG: Using airport_fetcher fallback for {selected_airport}: {target_lat}, {target_lon}")
                else:
                    print(f"WARNING: Airport {selected_airport} not found in loaded SCT data or OurAirports database. Using fallback position near equator.")
                    target_lat = 0.0
                    target_lon = 0.0
            except Exception as e:
                print(f"WARNING: Airport {selected_airport} not found in loaded SCT data. Using fallback position near equator. Error: {str(e)}")
                target_lat = 0.0
                target_lon = 0.0

        # Generate position between min_miles and max_miles
        # Convert miles to nautical miles for calculation
        min_nm = min_miles / 1.15078
        max_nm = max_miles / 1.15078
        bearing = random.uniform(0, 360)  # Random compass bearing
        distance_nm = random.uniform(min_nm, max_nm)  # Distance in nautical miles
        distance_deg = distance_nm * 0.01666  # Convert to degrees (rough approximation)

        # Calculate new position using basic trigonometry
        # More accurate calculation would use great circle distance, but this is close enough
        lat_offset = distance_deg * math.cos(math.radians(bearing))
        lon_offset = distance_deg * math.sin(math.radians(bearing)) / math.cos(math.radians(target_lat))

        new_lat = target_lat + lat_offset
        new_lon = target_lon + lon_offset

        # Clamp to valid ranges
        new_lat = max(-90, min(90, new_lat))
        new_lon = ((new_lon + 180) % 360) - 180

        return new_lat, new_lon
    
    def generate_route_to_airport(self, target_airport):
        """Generate a route to target airport using actual runway and fix data"""
        # Validate airport
        if not target_airport:
            return "DCT"
        
        try:
            route_parts = []
            
            # Get fixes from SCT parser if available
            fixes = []
            if self.creator and self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
                data = self.creator.sct_parser.get_data()
                if 'fixes' in data:
                    fixes = [fix['name'] for fix in data['fixes'] if 'name' in fix]
            
            # If we have fixes, use them
            if fixes:
                num_fixes = random.randint(1, min(3, len(fixes)))
                selected_fixes = random.sample(fixes, num_fixes)
                route_parts.extend(selected_fixes)
            
            # Try to get runway designators from SCT parser
            runway_designators = []
            if self.creator and self.creator.sct_parser and hasattr(self.creator.sct_parser, 'runways'):
                # Extract runway numbers from parsed runway data
                try:
                    if hasattr(self.creator.sct_parser, 'get_data'):
                        data = self.creator.sct_parser.get_data()
                        if 'runways' in data and isinstance(data['runways'], list):
                            # Try to extract runway designators from list
                            for rwy in data['runways']:
                                if isinstance(rwy, dict) and 'number' in rwy:
                                    runway_designators.append(rwy['number'])
                                elif hasattr(rwy, 'number'):
                                    # It's an object with .number attribute
                                    runway_designators.append(rwy.number)
                except:
                    pass
            
            # Fallback: if no runway data, use compass directions
            if not runway_designators:
                runway_designators = ['09', '27', '18', '36']
            
            # Pick a random runway
            runway_str = random.choice(runway_designators)
            route_parts.append(runway_str)
            
            # Return route or fallback to DCT
            if route_parts:
                return ' '.join(route_parts)
            else:
                return "DCT"
        
        except Exception as e:
            print(f"DEBUG: Route generation error: {e}")
            return "DCT"

    def generate_random_route(self):
        """Generate random route using current airport if available"""
        try:
            # Try to get selected airport from map viewer
            selected_airport = None
            if self.creator and hasattr(self.creator, 'map_viewer'):
                selected_airport = self.creator.map_viewer.get_selected_airport()
            
            if selected_airport:
                return self.generate_route_to_airport(selected_airport)
            else:
                return "DCT"
        except Exception:
            return "DCT"
    
    def generate_aircraft_at_entry_fixes(self, entry_fixes, airport_icao):
        """Generate aircraft at entry fixes within 50-75 miles of the airport"""
        if not entry_fixes:
            return []

        # Get target airport coordinates
        target_lat = None
        target_lon = None
        if self.creator.sct_parser and hasattr(self.creator.sct_parser, 'get_data'):
            data = self.creator.sct_parser.get_data()
            if 'airports' in data and data['airports']:
                for airport in data['airports']:
                    if airport.get('icao', '').upper() == airport_icao.upper():
                        if 'latitude' in airport and 'longitude' in airport:
                            target_lat = airport['latitude']
                            target_lon = airport['longitude']
                            break

        if not target_lat or not target_lon:
            print(f"Could not find coordinates for airport {airport_icao}")
            return []

        # Filter fixes within 50-75 miles of the airport
        valid_fixes = []
        for fix in entry_fixes:
            try:
                distance = self.calculate_distance(fix['lat'], fix['lon'], target_lat, target_lon)
                if 50 <= distance <= 75:
                    fix['distance_nm'] = distance  # Store calculated distance
                    valid_fixes.append(fix)
            except Exception as e:
                print(f"Error calculating distance for fix {fix.get('name', 'unknown')}: {e}")
                continue

        if not valid_fixes:
            print(f"No entry fixes found within 50-75 miles of {airport_icao}")
            return []

        aircraft_list = []

        # Generate 3-8 aircraft at random valid entry fixes
        num_aircraft = random.randint(3, min(8, len(valid_fixes)))
        selected_fixes = random.sample(valid_fixes, num_aircraft)

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
            distance = fix['distance_nm']
            if distance < 30:
                altitude = random.choice([5000, 6000, 7000])
            elif distance < 60:
                altitude = random.choice([8000, 10000, 12000])
            else:
                altitude = random.choice([14000, 16000, 18000])

            # Generate route to airport
            route = self.generate_route_from_fix_to_airport(fix['name'], airport_icao)

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
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in nautical miles"""
        import math

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        # Earth's radius in nautical miles
        R = 3440.065
        distance = R * c

        return distance

    def generate_route_from_fix_to_airport(self, fix_name, airport_icao):
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
