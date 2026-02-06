import re

class RWYParser:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.runways = []
        self.ils_data = []
        self.centerlines = []  # Store runway centerlines
        
    def parse(self, file_path=None):
        if file_path:
            self.file_path = file_path
            
        if not self.file_path:
            raise ValueError("No RWY file path provided")
        
        with open(self.file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith(';'):
                continue
            
            # Parse ILS definitions
            if line.startswith('ILS'):
                self.parse_ils_line(line)
            
            # Parse runway extended centerlines
            elif line.startswith('RWY_EXT'):
                self.parse_rwy_ext_line(line)
            
            # Parse runway definitions
            elif line.startswith('RWY:'):
                self.parse_rwy_line(line)
            
            # Parse SID/STAR centerlines
            elif any(x in line for x in ['CENTERLINE', 'CLINE']):
                self.parse_centerline_line(line)
        
        return self.get_data()
    
    def parse_ils_line(self, line):
        """Parse ILS line: ILS21L:-26.1358683:28.2571240:-26.1649203:28.2479394"""
        parts = line.split(':')
        if len(parts) >= 5:
            try:
                ils_name = parts[0]  # e.g., ILS21L
                glideslope_lat = float(parts[1])
                glideslope_lon = float(parts[2])
                localizer_lat = float(parts[3])
                localizer_lon = float(parts[4])
                
                runway_num = ils_name.replace('ILS', '')
                
                self.ils_data.append({
                    'name': ils_name,
                    'runway': runway_num,
                    'glideslope': (glideslope_lat, glideslope_lon),
                    'localizer': (localizer_lat, localizer_lon),
                    'type': 'ILS'
                })
                
            except (ValueError, IndexError):
                pass
    
    def parse_rwy_ext_line(self, line):
        """Parse runway extended centerline: RWY_EXT:21L:coord1:coord2:..."""
        parts = line.split(':')
        if len(parts) >= 4:
            try:
                rwy_num = parts[1]
                coordinates = []
                
                for i in range(2, len(parts)-1, 2):
                    lat = float(parts[i])
                    lon = float(parts[i+1])
                    coordinates.append((lat, lon))
                
                if coordinates:
                    runway_data = {
                        'number': rwy_num,
                        'type': 'EXTENDED_CENTERLINE',
                        'coordinates': coordinates,
                        'extended': True
                    }
                    self.runways.append(runway_data)
                    
                    # Also add to centerlines
                    self.centerlines.append({
                        'name': f"RWY{rwy_num}",
                        'coordinates': coordinates,
                        'type': 'RUNWAY_CENTERLINE'
                    })
                    
            except (ValueError, IndexError):
                pass
    
    def parse_rwy_line(self, line):
        """Parse standard runway definition"""
        if line.startswith('RWY:'):
            parts = line.split(':')
            if len(parts) >= 4:
                try:
                    rwy_num = parts[1]
                    coordinates = []
                    
                    for i in range(2, len(parts)-1, 2):
                        lat = float(parts[i])
                        lon = float(parts[i+1])
                        coordinates.append((lat, lon))
                    
                    if coordinates:
                        runway_data = {
                            'number': rwy_num,
                            'type': 'RUNWAY',
                            'coordinates': coordinates,
                            'extended': False
                        }
                        self.runways.append(runway_data)
                        
                        # Also add to centerlines
                        self.centerlines.append({
                            'name': f"RWY{rwy_num}",
                            'coordinates': coordinates,
                            'type': 'RUNWAY'
                        })
                        
                except (ValueError, IndexError):
                    pass
    
    def parse_centerline_line(self, line):
        """Parse centerline definitions"""
        # Look for patterns like: CENTERLINE:name:coord1:coord2:...
        if 'CENTERLINE' in line or 'CLINE' in line:
            parts = line.split(':')
            if len(parts) >= 4:
                try:
                    name = parts[1]
                    coordinates = []
                    
                    for i in range(2, len(parts)-1, 2):
                        lat = float(parts[i])
                        lon = float(parts[i+1])
                        coordinates.append((lat, lon))
                    
                    if coordinates:
                        self.centerlines.append({
                            'name': name,
                            'coordinates': coordinates,
                            'type': 'CENTERLINE'
                        })
                        
                except (ValueError, IndexError):
                    pass
    
    def get_ils_for_runway(self, runway_number):
        """Get ILS data for specific runway"""
        for ils in self.ils_data:
            if ils['runway'] == runway_number:
                return ils
        return None
    
        def get_extended_centerlines(self):
            """Get all extended centerlines"""
            return [rwy for rwy in self.runways if rwy.get('extended', False)]
    
        def get_runways(self):
            """Get all runways"""
            return self.runways

        def get_ils_data(self):
            """Get all ILS data"""
            return self.ils_data

        def get_centerlines(self):
            """Get all centerlines"""
            return self.centerlines

        def get_data(self):
            return {
                'runways': self.runways,
                'ils_data': self.ils_data,
                'centerlines': self.centerlines
            }