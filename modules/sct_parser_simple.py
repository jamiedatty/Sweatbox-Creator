import re

class SCTParser:
    def __init__(self, sct_filepath):
        self.sct_filepath = sct_filepath
        self.data = {
            'airports': [],
            'fixes': [],
            'airspace_lines': [],
            'labels': [],
            'geo': [],
            'regions': []
        }
        self.parse()
    
    def parse(self):
        try:
            with open(self.sct_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_section = None
            section_content = []
            
            for line in lines:
                stripped = line.strip()
                
                if stripped.startswith('[') and stripped.endswith(']'):
                    if current_section and section_content:
                        self._process_section(current_section, section_content)
                    
                    current_section = stripped[1:-1].strip().upper()
                    section_content = []
                else:
                    if stripped and not stripped.startswith(';'):
                        section_content.append(line)
            
            if current_section and section_content:
                self._process_section(current_section, section_content)
                
        except Exception as e:
            print(f"SCT parsing error: {e}")
    
    def _process_section(self, section_name, content):
        if section_name == 'AIRPORTS':
            self.data['airports'] = self._parse_airports(content)
        elif section_name == 'FIXES':
            self.data['fixes'] = self._parse_fixes(content)
        elif section_name in ['ARTCC', 'ARTCC LOW', 'ARTCC HIGH']:
            self.data['airspace_lines'].extend(self._parse_airspace(content, section_name))
        elif section_name == 'GEO':
            self.data['geo'].extend(content)
        elif section_name == 'REGIONS':
            self.data['regions'].extend(content)
        elif section_name == 'LABELS':
            self.data['labels'].extend(content)
    
    def _parse_airports(self, content):
        airports = []
        for line in content:
            parts = line.strip().split()
            if len(parts) >= 3:
                airport = {
                    'icao': parts[0],
                    'latitude': self._parse_coordinate(parts[1]),
                    'longitude': self._parse_coordinate(parts[2])
                }
                if len(parts) > 3:
                    airport['name'] = ' '.join(parts[3:])
                airports.append(airport)
        return airports
    
    def _parse_fixes(self, content):
        fixes = []
        for line in content:
            parts = line.strip().split()
            if len(parts) >= 3:
                fix = {
                    'name': parts[0],
                    'latitude': self._parse_coordinate(parts[1]),
                    'longitude': self._parse_coordinate(parts[2])
                }
                fixes.append(fix)
        return fixes
    
    def _parse_airspace(self, content, airspace_type):
        lines = []
        current_line = []
        
        for line in content:
            stripped = line.strip()
            if not stripped:
                if current_line:
                    lines.append({
                        'type': airspace_type,
                        'coordinates': current_line
                    })
                    current_line = []
                continue
            
            coords = self._parse_coordinate_pair(stripped)
            if coords:
                current_line.append(coords)
        
        if current_line:
            lines.append({
                'type': airspace_type,
                'coordinates': current_line
            })
        
        return lines
    
    def _parse_coordinate(self, coord_str):
        try:
            if 'N' in coord_str or 'S' in coord_str:
                return self._parse_latlon_coordinate(coord_str)
            else:
                return float(coord_str)
        except:
            return None
    
    def _parse_latlon_coordinate(self, coord_str):
        coord_str = coord_str.upper().replace(' ', '')
        
        if 'N' in coord_str:
            parts = coord_str.split('N')
            deg = float(parts[0])
            if "'" in parts[1]:
                min_sec = parts[1].split("'")
                minutes = float(min_sec[0])
                if '"' in min_sec[1]:
                    seconds = float(min_sec[1].split('"')[0])
                else:
                    seconds = 0
            else:
                minutes = 0
                seconds = 0
            
            lat = deg + minutes/60 + seconds/3600
            return lat
        
        elif 'S' in coord_str:
            parts = coord_str.split('S')
            deg = float(parts[0])
            if "'" in parts[1]:
                min_sec = parts[1].split("'")
                minutes = float(min_sec[0])
                if '"' in min_sec[1]:
                    seconds = float(min_sec[1].split('"')[0])
                else:
                    seconds = 0
            else:
                minutes = 0
                seconds = 0
            
            lat = -(deg + minutes/60 + seconds/3600)
            return lat
        
        elif 'E' in coord_str:
            parts = coord_str.split('E')
            deg = float(parts[0])
            if "'" in parts[1]:
                min_sec = parts[1].split("'")
                minutes = float(min_sec[0])
                if '"' in min_sec[1]:
                    seconds = float(min_sec[1].split('"')[0])
                else:
                    seconds = 0
            else:
                minutes = 0
                seconds = 0
            
            lon = deg + minutes/60 + seconds/3600
            return lon
        
        elif 'W' in coord_str:
            parts = coord_str.split('W')
            deg = float(parts[0])
            if "'" in parts[1]:
                min_sec = parts[1].split("'")
                minutes = float(min_sec[0])
                if '"' in min_sec[1]:
                    seconds = float(min_sec[1].split('"')[0])
                else:
                    seconds = 0
            else:
                minutes = 0
                seconds = 0
            
            lon = -(deg + minutes/60 + seconds/3600)
            return lon
        
        return None
    
    def _parse_coordinate_pair(self, coord_str):
        parts = coord_str.split()
        if len(parts) >= 2:
            lat = self._parse_coordinate(parts[0])
            lon = self._parse_coordinate(parts[1])
            if lat is not None and lon is not None:
                return (lat, lon)
        return None
    
    def get_data(self):
        return self.data