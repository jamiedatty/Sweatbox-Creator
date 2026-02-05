"""
SCT Parser Module
Parses EuroScope Sector Files (.sct)
"""
import re
from typing import Dict, List, Tuple, Optional

class SCTParser:
    def __init__(self, sct_filepath):
        self.sct_filepath = sct_filepath
        self.data = {
            'airspace': [],
            'vor': [],
            'ndb': [],
            'fixes': [],
            'airports': [],
            'runways': [],
            'artcc': [],
            'high_airways': [],
            'low_airways': []
        }
        self.parse()
    
    def parse(self):
        try:
            with open(self.sct_filepath, 'r', encoding='latin-1') as f:
                content = f.read()
            
            # Parse different sections
            lines = content.split('\n')
            self._parse_sections(lines)
            
        except Exception as e:
            print(f"Error parsing SCT file: {e}")
    
    def _parse_sections(self, lines):
        current_section = None
        section_data = []
        
        for line in lines:
            line = line.strip()
            
            # Check for section header
            if line.startswith('[') and line.endswith(']'):
                # Save previous section data
                if current_section and section_data:
                    self._process_section(current_section, section_data)
                
                # Start new section
                current_section = line[1:-1].upper()
                section_data = []
            else:
                section_data.append(line)
        
        # Process last section
        if current_section and section_data:
            self._process_section(current_section, section_data)
    
    def _process_section(self, section_name, section_data):
        if section_name == 'INFO':
            self._parse_info(section_data)
        elif section_name == 'VOR':
            self._parse_vor(section_data)
        elif section_name == 'NDB':
            self._parse_ndb(section_data)
        elif section_name == 'AIRPORT':
            self._parse_airport(section_data)
        elif section_name == 'RUNWAY':
            self._parse_runway(section_data)
        elif section_name == 'FIXES':
            self._parse_fixes(section_data)
        elif section_name == 'ARTCC':
            self._parse_artcc(section_data)
        elif section_name == 'HIGH AIRWAY':
            self._parse_high_airway(section_data)
        elif section_name == 'LOW AIRWAY':
            self._parse_low_airway(section_data)
        elif section_name in ['GEO', 'LATLONG', 'REGIONS']:
            self._parse_airspace(section_name, section_data)
    
    def _parse_info(self, data):
        info = {}
        for line in data:
            if '=' in line:
                key, value = line.split('=', 1)
                info[key.strip()] = value.strip()
        self.data['info'] = info
    
    def _parse_vor(self, data):
        for line in data:
            if line and not line.startswith(';'):
                vor = self._parse_navaid_line(line, 'VOR')
                if vor:
                    self.data['vor'].append(vor)
    
    def _parse_ndb(self, data):
        for line in data:
            if line and not line.startswith(';'):
                ndb = self._parse_navaid_line(line, 'NDB')
                if ndb:
                    self.data['ndb'].append(ndb)
    
    def _parse_navaid_line(self, line, navaid_type):
        parts = line.split()
        if len(parts) >= 3:
            try:
                ident = parts[0]
                lat = self._parse_dms(parts[1])
                lon = self._parse_dms(parts[2])
                
                navaid = {
                    'type': navaid_type,
                    'identifier': ident,
                    'lat': lat,
                    'lon': lon,
                    'name': ident
                }
                
                if len(parts) > 3:
                    if navaid_type == 'VOR':
                        navaid['frequency'] = parts[3]
                    elif navaid_type == 'NDB':
                        navaid['frequency'] = parts[3]
                    
                    if len(parts) > 4:
                        navaid['name'] = ' '.join(parts[4:])
                
                return navaid
            except (ValueError, IndexError):
                return None
        return None
    
    def _parse_airport(self, data):
        for line in data:
            if line and not line.startswith(';'):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        icao = parts[0]
                        lat = self._parse_dms(parts[1])
                        lon = self._parse_dms(parts[2])
                        
                        airport = {
                            'type': 'AIRPORT',
                            'icao': icao,
                            'lat': lat,
                            'lon': lon,
                            'name': icao
                        }
                        
                        if len(parts) > 3:
                            airport['elevation'] = parts[3]
                        if len(parts) > 4:
                            airport['name'] = ' '.join(parts[4:])
                        
                        self.data['airports'].append(airport)
                    except (ValueError, IndexError):
                        continue
    
    def _parse_runway(self, data):
        for line in data:
            if line and not line.startswith(';'):
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        runway = {
                            'airport': parts[0],
                            'number': parts[1],
                            'lat': self._parse_dms(parts[2]),
                            'lon': self._parse_dms(parts[3]),
                            'length': parts[4],
                            'width': parts[5]
                        }
                        
                        if len(parts) > 6:
                            runway['surface'] = parts[6]
                        
                        self.data['runways'].append(runway)
                    except (ValueError, IndexError):
                        continue
    
    def _parse_fixes(self, data):
        for line in data:
            if line and not line.startswith(';'):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        ident = parts[0]
                        lat = self._parse_dms(parts[1])
                        lon = self._parse_dms(parts[2])
                        
                        fix = {
                            'type': 'FIX',
                            'identifier': ident,
                            'lat': lat,
                            'lon': lon,
                            'name': ident
                        }
                        
                        if len(parts) > 3:
                            fix['name'] = ' '.join(parts[3:])
                        
                        self.data['fixes'].append(fix)
                    except (ValueError, IndexError):
                        continue
    
    def _parse_artcc(self, data):
        artcc = {'name': '', 'coordinates': []}
        
        for line in data:
            if line.startswith(';'):
                if 'name' in artcc and artcc['coordinates']:
                    self.data['artcc'].append(artcc.copy())
                artcc = {'name': line[1:].strip(), 'coordinates': []}
            elif line and not line.startswith(';'):
                coords = self._parse_coordinate_line(line)
                if coords:
                    artcc['coordinates'].extend(coords)
        
        if 'name' in artcc and artcc['coordinates']:
            self.data['artcc'].append(artcc)
    
    def _parse_airspace(self, section_name, data):
        airspace = {
            'section': section_name,
            'name': '',
            'type': self._detect_airspace_type(section_name),
            'class': self._extract_airspace_class(section_name),
            'floor': 'GND',
            'ceiling': 'UNL',
            'coordinates': []
        }
        
        for line in data:
            if line.startswith(';'):
                if airspace['name'] and airspace['coordinates']:
                    self.data['airspace'].append(airspace.copy())
                airspace = {
                    'section': section_name,
                    'name': line[1:].strip(),
                    'type': self._detect_airspace_type(section_name),
                    'class': self._extract_airspace_class(section_name),
                    'floor': 'GND',
                    'ceiling': 'UNL',
                    'coordinates': []
                }
            elif line and not line.startswith(';'):
                # Check for altitude information
                if any(x in line.upper() for x in ['FL', 'F', 'GND', 'UNL', 'SFC', 'MSL']):
                    # Parse altitude
                    if 'GND' in line.upper() or 'SFC' in line.upper():
                        airspace['floor'] = 'GND'
                    elif 'UNL' in line.upper():
                        airspace['ceiling'] = 'UNL'
                    else:
                        # Parse flight level
                        fl_match = re.search(r'FL?(\d+)', line.upper())
                        if fl_match:
                            if airspace['floor'] == 'GND':
                                airspace['floor'] = f"FL{fl_match.group(1)}"
                            else:
                                airspace['ceiling'] = f"FL{fl_match.group(1)}"
                else:
                    # Parse coordinates
                    coords = self._parse_coordinate_line(line)
                    if coords:
                        airspace['coordinates'].extend(coords)
        
        if airspace['name'] and airspace['coordinates']:
            self.data['airspace'].append(airspace)
    
    def _parse_high_airway(self, data):
        self._parse_airway(data, 'HIGH')
    
    def _parse_low_airway(self, data):
        self._parse_airway(data, 'LOW')
    
    def _parse_airway(self, data, airway_type):
        airway = {'type': airway_type, 'name': '', 'segments': []}
        current_segment = []
        
        for line in data:
            if line.startswith(';'):
                if airway['name'] and airway['segments']:
                    self.data[f'{airway_type.lower()}_airways'].append(airway.copy())
                airway = {'type': airway_type, 'name': line[1:].strip(), 'segments': []}
                current_segment = []
            elif line and not line.startswith(';'):
                parts = line.split()
                if len(parts) >= 2:
                    ident = parts[0]
                    lat = self._parse_dms(parts[1])
                    lon = self._parse_dms(parts[2])
                    
                    current_segment.append({
                        'identifier': ident,
                        'lat': lat,
                        'lon': lon
                    })
                    
                    if len(current_segment) >= 2:
                        airway['segments'].append(current_segment.copy())
                        current_segment = [current_segment[-1]]  # Continue from last point
        
        if airway['name'] and airway['segments']:
            self.data[f'{airway_type.lower()}_airways'].append(airway)
    
    def _parse_coordinate_line(self, line):
        coords = []
        parts = line.split()
        
        for part in parts:
            if ',' in part:
                lat_str, lon_str = part.split(',', 1)
                try:
                    lat = self._parse_dms(lat_str)
                    lon = self._parse_dms(lon_str)
                    coords.append({'lat': lat, 'lon': lon})
                except ValueError:
                    continue
        
        return coords
    
    def _parse_dms(self, dms_str):
        """Parse Degrees, Minutes, Seconds to decimal degrees"""
        dms_str = dms_str.strip().upper()
        
        # Handle N/S/E/W suffixes
        hemisphere = None
        if dms_str.endswith('N'):
            hemisphere = 'N'
            dms_str = dms_str[:-1]
        elif dms_str.endswith('S'):
            hemisphere = 'S'
            dms_str = dms_str[:-1]
        elif dms_str.endswith('E'):
            hemisphere = 'E'
            dms_str = dms_str[:-1]
        elif dms_str.endswith('W'):
            hemisphere = 'W'
            dms_str = dms_str[:-1]
        
        # Split by dots
        parts = dms_str.split('.')
        
        if len(parts) >= 3:
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            
            decimal = degrees + minutes/60 + seconds/3600
            
            if hemisphere in ['S', 'W']:
                decimal = -decimal
            
            return decimal
        
        # Try simple float conversion
        try:
            decimal = float(dms_str)
            if hemisphere in ['S', 'W']:
                decimal = -decimal
            return decimal
        except ValueError:
            return 0.0
    
    def _detect_airspace_type(self, name):
        name_upper = name.upper()
        
        if 'CTR' in name_upper:
            return 'CTR'
        elif 'TMA' in name_upper:
            return 'TMA'
        elif 'CTA' in name_upper:
            return 'CTA'
        elif 'CLASS' in name_upper:
            return 'CLASS'
        elif 'FIR' in name_upper:
            return 'FIR'
        elif 'UIR' in name_upper:
            return 'UIR'
        elif 'ARTCC' in name_upper:
            return 'ARTCC'
        else:
            return 'OTHER'
    
    def _extract_airspace_class(self, name):
        name_upper = name.upper()
        
        for cls in ['CLASS A', 'CLASS B', 'CLASS C', 'CLASS D', 'CLASS E', 'CLASS F', 'CLASS G']:
            if cls in name_upper:
                return cls.split()[1]
        
        if 'CTR' in name_upper:
            return 'D'
        elif 'TMA' in name_upper or 'CTA' in name_upper:
            return 'C'
        elif 'FIR' in name_upper or 'UIR' in name_upper or 'ARTCC' in name_upper:
            return 'E'
        
        return 'UNKNOWN'
    
    def get_data(self):
        return self.data
    
    def get_airspace_classes(self):
        classes = {}
        for airspace in self.data['airspace']:
            cls = airspace.get('class', 'UNKNOWN')
            if cls not in classes:
                classes[cls] = []
            classes[cls].append(airspace)
        return classes