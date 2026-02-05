import re

class ESEParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {
            'positions': [],
            'sidsstars': [],
            'airspace': [],
            'radar': [],
            'freetext': []
        }
        self.parse()
    
    def parse(self):
        with open(self.filepath, 'r', encoding='latin-1') as f:
            content = f.read()
        
        sections = self._split_sections(content)
        
        for section_name, section_content in sections.items():
            if section_name == 'POSITIONS':
                self.data['positions'] = self._parse_positions(section_content)
            elif section_name == 'SIDSSTARS':
                self.data['sidsstars'] = self._parse_sidsstars(section_content)
            elif section_name == 'AIRSPACE':
                self.data['airspace'] = self._parse_airspace(section_content)
            elif section_name == 'RADAR':
                self.data['radar'] = self._parse_radar(section_content)
            elif section_name == 'FREETEXT':
                self.data['freetext'] = self._parse_freetext(section_content)
    
    def _split_sections(self, content):
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.strip().startswith('[') and line.strip().endswith(']'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                current_section = line.strip()[1:-1]
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_positions(self, content):
        positions = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            parts = line.split(':')
            if len(parts) >= 11:
                position = {
                    'callsign': parts[0],
                    'name': parts[1],
                    'frequency': parts[2],
                    'identifier': parts[3],
                    'prefix': parts[4],
                    'suffix': parts[5],
                    'type': parts[6],
                    'mid': parts[7],
                    'vis_center1': parts[10] if len(parts) > 10 else '',
                    'vis_center2': parts[11] if len(parts) > 11 else '',
                }
                
                coords = []
                for i in range(10, len(parts)):
                    if self._is_coordinate(parts[i]):
                        coords.append(parts[i])
                position['coordinates'] = coords
                
                positions.append(position)
        
        return positions
    
    def _parse_sidsstars(self, content):
        sidsstars = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            parts = line.split(':')
            if len(parts) >= 4:
                sidsstar = {
                    'type': parts[0],
                    'airport': parts[1],
                    'runway': parts[2],
                    'name': parts[3],
                    'waypoints': parts[4].split() if len(parts) > 4 else []
                }
                sidsstars.append(sidsstar)
        
        return sidsstars
    
    def _parse_airspace(self, content):
        airspace = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            airspace.append(line)
        return airspace
    
    def _parse_radar(self, content):
        radar = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            radar.append(line)
        return radar
    
    def _parse_freetext(self, content):
        freetext = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            freetext.append(line)
        return freetext
    
    def _is_coordinate(self, text):
        return bool(re.match(r'^[NS]\d+\.\d+\.\d+\.\d+$', text, re.IGNORECASE) or
                   re.match(r'^[EW]\d+\.\d+\.\d+\.\d+$', text, re.IGNORECASE))
    
    def get_positions(self):
        return self.data['positions']
    
    def get_sidsstars(self):
        return self.data['sidsstars']
    
    def get_all_coordinates(self):
        coordinates = []
        for position in self.data['positions']:
            if 'coordinates' in position:
                lat = None
                lon = None
                
                for coord in position['coordinates']:
                    parsed = self._parse_coordinate(coord)
                    if parsed:
                        if parsed[0] is not None:
                            lat = parsed[0]
                        if parsed[1] is not None:
                            lon = parsed[1]
                
                if lat is not None and lon is not None:
                    coordinates.append({
                        'lat': lat,
                        'lon': lon,
                        'name': position['callsign']
                    })
        return coordinates
    
    def _parse_coordinate(self, coord_str):
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