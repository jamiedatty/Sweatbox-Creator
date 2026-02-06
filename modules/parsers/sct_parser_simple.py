import re
import json
import os
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class SCTSectionType(Enum):
    INFO = "INFO"
    VOR = "VOR"
    NDB = "NDB"
    RUNWAY = "RUNWAY"
    TAXIWAY = "TAXIWAY"
    FREQUENCY = "FREQUENCY"
    SIDS = "SIDS"
    STARS = "STARS"
    APPROACHES = "APPROACHES"
    REGIONS = "REGIONS"
    COLOR = "COLOR"
    GEO = "GEO"
    ARTCC = "ARTCC"
    ARTCC_HIGH = "ARTCC HIGH"
    ARTCC_LOW = "ARTCC LOW"

@dataclass
class Coordinate:
    lat: float
    lon: float

@dataclass
class Runway:
    number: str
    heading: float
    length: int
    width: int
    surface: str
    ils: Optional[float]
    coordinates: List[Coordinate]

@dataclass
class Frequency:
    type: str
    name: str
    freq: float

@dataclass
class Navaid:
    id: str
    name: str
    freq: Optional[float]
    coord: Coordinate
    type: str

class SCTParser:
    # Pre-compiled regex patterns for efficiency
    _COORD_PATTERN = re.compile(r'([NS])(\d+)\.(\d+)\.(\d+)\.(\d+)')
    _SECTION_PATTERN = re.compile(r'^\[([^\]]+)\]$')
    _VERSION_PATTERN = re.compile(r'VERSION\s+(\d+\.\d+)', re.IGNORECASE)
    _ILS_PATTERN = re.compile(r'ILS\s+(\d+\.\d+)')
    _FREQ_PATTERN_VOR = re.compile(r'(\d+\.\d+)')
    _FREQ_PATTERN_NDB = re.compile(r'(\d+)')
    
    def __init__(self, file_path: Optional[str] = None, ese_name: Optional[str] = None):
        self.file_path = file_path
        self.ese_name = ese_name
        self.raw_data: Dict[str, List[str]] = {}
        self.parsed_data: Dict[str, Any] = {}
        self.metadata: Dict[str, str] = {}
        self.runways: List[Runway] = []
        self.frequencies: List[Frequency] = []
        self.vors: List[Navaid] = []
        self.ndbs: List[Navaid] = []
        self.taxiways: List[List[Coordinate]] = []
        self.airports: List[Dict] = []
        self.fixes: List[Dict] = []
        self.artcc_high_boundaries: List[Dict] = []
        self.artcc_low_boundaries: List[Dict] = []
        self.version: str = ""
        self.cache_dir = "cache"
        
        # Coordinate cache for performance
        self._coord_cache: Dict[str, Optional[Tuple[float, float]]] = {}
        
    def _get_cache_filename(self) -> str:
        """Generate cache filename based on ESE name and file hash"""
        if not self.file_path:
            return None
            
        prefix = self.ese_name[:4].upper() if self.ese_name else "SECT"
        file_hash = hashlib.md5(self.file_path.encode()).hexdigest()[:8]
        return f"{prefix}-{file_hash}-cache.json"
    
    def _load_from_cache(self) -> bool:
        """Try to load data from cache file"""
        cache_file = self._get_cache_filename()
        if not cache_file:
            return False
            
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        if not os.path.exists(cache_path):
            return False
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            self.artcc_high_boundaries = cached_data.get('ARTCC_HIGH', [])
            self.artcc_low_boundaries = cached_data.get('ARTCC_LOW', [])
            
            print(f"Loaded from cache: {cache_file}")
            return True
            
        except Exception:
            return False
    
    def _save_to_cache(self):
        """Save boundary data to cache file"""
        cache_file = self._get_cache_filename()
        if not cache_file:
            return
            
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        cache_data = {
            'ARTCC_HIGH': self.artcc_high_boundaries,
            'ARTCC_LOW': self.artcc_low_boundaries,
            'source_file': self.file_path,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'cache_version': '1.0'
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"Saved to cache: {cache_file}")
        except Exception:
            pass
        
    def parse(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        if file_path:
            self.file_path = file_path
            
        if not self.file_path:
            raise ValueError("No SCT file path provided")
        
        # Try to load from cache first
        cache_loaded = self._load_from_cache()
        
        # Parse file content
        with open(self.file_path, 'r', encoding='latin-1') as f:
            content = f.read()
            
        self._parse_raw_sections(content)
        
        # Only parse boundaries if not loaded from cache
        if not cache_loaded:
            self._parse_artcc_boundaries()
            self._save_to_cache()
        
        # Parse other sections
        self._extract_metadata()
        self._parse_runways()
        self._parse_frequencies()
        self._parse_navaids()
        self._parse_taxiways()
        self._parse_airports()
        self._parse_fixes()
        self._parse_version()
        
        # Build final parsed data
        self.parsed_data = {
            'metadata': self.metadata,
            'runways': [r.__dict__ for r in self.runways],
            'frequencies': [f.__dict__ for f in self.frequencies],
            'VOR': [{'latitude': v.coord.lat, 'longitude': v.coord.lon, 'name': v.name, 'id': v.id} for v in self.vors],
            'NDB': [{'latitude': n.coord.lat, 'longitude': n.coord.lon, 'name': n.name, 'id': n.id} for n in self.ndbs],
            'taxiways': self.taxiways,
            'airports': self.airports,
            'fixes': self.fixes,
            'ARTCC_HIGH': self.artcc_high_boundaries,
            'ARTCC_LOW': self.artcc_low_boundaries,
            'version': self.version,
            'raw_sections': self.raw_data
        }
        
        return self.parsed_data
    
    def _parse_coordinate_fast(self, coord_str: str) -> Optional[Tuple[float, float]]:
        """Optimized coordinate parsing with caching"""
        if coord_str in self._coord_cache:
            return self._coord_cache[coord_str]
        
        coord_str = coord_str.strip()
        
        # Try N/S E/W format
        match = self._COORD_PATTERN.findall(coord_str)
        if len(match) == 2:
            lat_match, lon_match = match
            lat_dir, lat_deg, lat_min, lat_sec, lat_frac = lat_match
            lon_dir, lon_deg, lon_min, lon_sec, lon_frac = lon_match
            
            # Fast calculation
            lat = float(lat_deg) + float(lat_min)/60 + (float(lat_sec) + float(lat_frac)/1000)/3600
            if lat_dir == 'S':
                lat = -lat
                
            lon = float(lon_deg) + float(lon_min)/60 + (float(lon_sec) + float(lon_frac)/1000)/3600
            if lon_dir == 'W':
                lon = -lon
            
            result = (lat, lon)
            self._coord_cache[coord_str] = result
            return result
        
        # Try decimal format
        parts = coord_str.split()
        if len(parts) == 2:
            try:
                result = (float(parts[0]), float(parts[1]))
                self._coord_cache[coord_str] = result
                return result
            except ValueError:
                pass
        
        self._coord_cache[coord_str] = None
        return None
    
    def _parse_artcc_boundaries(self):
        """Parse ARTCC boundaries"""
        # Parse ARTCC HIGH
        if 'ARTCC HIGH' in self.raw_data or 'ARTCC_HIGH' in self.raw_data:
            section_data = self.raw_data.get('ARTCC HIGH', self.raw_data.get('ARTCC_HIGH', []))
            self.artcc_high_boundaries = self._parse_artcc_section_optimized(section_data)
        
        # Parse ARTCC LOW
        if 'ARTCC LOW' in self.raw_data or 'ARTCC_LOW' in self.raw_data:
            section_data = self.raw_data.get('ARTCC LOW', self.raw_data.get('ARTCC_LOW', []))
            self.artcc_low_boundaries = self._parse_artcc_section_optimized(section_data)
        
        # Also try generic ARTCC section
        if 'ARTCC' in self.raw_data:
            artcc_data = self._parse_artcc_section_optimized(self.raw_data['ARTCC'])
            if not self.artcc_low_boundaries:
                self.artcc_low_boundaries = artcc_data
    
    def _parse_artcc_section_optimized(self, lines: List[str]) -> List[Dict]:
        """Optimized ARTCC boundary parsing with line combination"""
        boundaries = []
        current_boundary = None
        current_path = []  # Track current continuous path
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a boundary name (not starting with coordinate pattern)
            if not line.startswith(('N', 'S', ' ')) and not line[0].isdigit():
                # End previous boundary
                if current_boundary:
                    # Add any remaining path segments
                    self._add_path_to_boundary(current_boundary, current_path)
                    boundaries.append(current_boundary)
                
                # Start new boundary
                current_boundary = {
                    'name': line,
                    'segments': []
                }
                current_path = []  # Reset current path
                continue
            
            # Parse coordinate line for current boundary
            if current_boundary is not None:
                # Split line into coordinate parts
                parts = line.split()
                
                # Process each pair of coordinates in the line
                for i in range(0, len(parts), 4):
                    if i + 3 >= len(parts):
                        break
                    
                    # Parse start and end coordinates
                    start_str = f"{parts[i]} {parts[i+1]}"
                    end_str = f"{parts[i+2]} {parts[i+3]}"
                    
                    start_coord = self._parse_coordinate_fast(start_str)
                    end_coord = self._parse_coordinate_fast(end_str)
                    
                    if not start_coord or not end_coord:
                        continue
                    
                    # Check if we can continue the current path
                    if not current_path:
                        # Start new path
                        current_path = [start_coord, end_coord]
                    elif self._coords_equal(current_path[-1], start_coord):
                        # Continue existing path
                        current_path.append(end_coord)
                    else:
                        # End current path and start new one
                        self._add_path_to_boundary(current_boundary, current_path)
                        current_path = [start_coord, end_coord]
        
        # Handle last boundary and path
        if current_boundary:
            self._add_path_to_boundary(current_boundary, current_path)
            boundaries.append(current_boundary)
        
        return boundaries
    
    def _coords_equal(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> bool:
        """Check if two coordinates are approximately equal"""
        return (abs(coord1[0] - coord2[0]) < 0.000001 and 
                abs(coord1[1] - coord2[1]) < 0.000001)
    
    def _add_path_to_boundary(self, boundary: Dict, path: List[Tuple[float, float]]):
        """Convert a continuous path into segments and add to boundary"""
        if len(path) < 2:
            return
        
        # Create segments from the path
        for i in range(len(path) - 1):
            boundary['segments'].append({
                'start': path[i],
                'end': path[i + 1]
            })
    
    def _parse_raw_sections(self, content: str):
        """Parse raw sections from content"""
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith(';'):
                continue
                
            section_match = self._SECTION_PATTERN.match(line)
            if section_match:
                current_section = section_match.group(1)
                self.raw_data[current_section] = []
                continue
                
            if current_section:
                self.raw_data[current_section].append(line)
    
    def _extract_metadata(self):
        """Extract metadata from INFO section"""
        if 'INFO' in self.raw_data:
            for line in self.raw_data['INFO']:
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.metadata[key.strip()] = value.strip()
    
    def _parse_airports(self):
        """Parse airport data"""
        if 'AIRPORT' in self.raw_data:
            for line in self.raw_data['AIRPORT']:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        self.airports.append({
                            'icao': parts[0],
                            'latitude': float(parts[1]),
                            'longitude': float(parts[2]),
                            'name': ' '.join(parts[3:]) if len(parts) > 3 else parts[0]
                        })
                    except ValueError:
                        continue
    
    def _parse_fixes(self):
        """Parse fix/waypoint data"""
        if 'FIXES' in self.raw_data:
            for line in self.raw_data['FIXES']:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        self.fixes.append({
                            'name': parts[0],
                            'latitude': float(parts[1]),
                            'longitude': float(parts[2])
                        })
                    except ValueError:
                        continue
    
    def _parse_runways(self):
        """Parse runway data"""
        if 'RUNWAY' not in self.raw_data:
            return
            
        for line in self.raw_data['RUNWAY']:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    rwy_num = parts[0]
                    heading = float(parts[1])
                    length = int(parts[2])
                    width = int(parts[3]) if len(parts) > 3 else 100
                    surface = parts[4] if len(parts) > 4 else "ASPH"
                    
                    coords = []
                    for i in range(5, len(parts)-1, 2):
                        try:
                            lat = float(parts[i])
                            lon = float(parts[i+1])
                            coords.append(Coordinate(lat, lon))
                        except ValueError:
                            continue
                    
                    ils = None
                    ils_match = self._ILS_PATTERN.search(line)
                    if ils_match:
                        ils = float(ils_match.group(1))
                    
                    self.runways.append(Runway(
                        number=rwy_num,
                        heading=heading,
                        length=length,
                        width=width,
                        surface=surface,
                        ils=ils,
                        coordinates=coords
                    ))
                except (ValueError, IndexError):
                    continue
    
    def _parse_frequencies(self):
        """Parse frequency data"""
        if 'FREQUENCY' not in self.raw_data:
            return
            
        for line in self.raw_data['FREQUENCY']:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    self.frequencies.append(Frequency(
                        type=parts[0],
                        name=parts[1],
                        freq=float(parts[2])
                    ))
                except ValueError:
                    continue
    
    def _parse_navaids(self):
        """Parse navaid data"""
        self._parse_vors()
        self._parse_ndbs()
    
    def _parse_vors(self):
        """Parse VOR data"""
        if 'VOR' not in self.raw_data:
            return
            
        for line in self.raw_data['VOR']:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    vor_id = parts[0]
                    lat = float(parts[1])
                    lon = float(parts[2])
                    name = ' '.join(parts[3:])
                    
                    freq = None
                    freq_match = self._FREQ_PATTERN_VOR.search(name)
                    if freq_match:
                        freq = float(freq_match.group(1))
                        name = name.replace(freq_match.group(0), '').strip()
                    
                    self.vors.append(Navaid(
                        id=vor_id,
                        name=name,
                        freq=freq,
                        coord=Coordinate(lat, lon),
                        type='VOR'
                    ))
                except ValueError:
                    continue
    
    def _parse_ndbs(self):
        """Parse NDB data"""
        if 'NDB' not in self.raw_data:
            return
            
        for line in self.raw_data['NDB']:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    ndb_id = parts[0]
                    lat = float(parts[1])
                    lon = float(parts[2])
                    name = ' '.join(parts[3:])
                    
                    freq = None
                    freq_match = self._FREQ_PATTERN_NDB.search(name)
                    if freq_match:
                        freq = float(freq_match.group(1))
                        name = name.replace(freq_match.group(0), '').strip()
                    
                    self.ndbs.append(Navaid(
                        id=ndb_id,
                        name=name,
                        freq=freq,
                        coord=Coordinate(lat, lon),
                        type='NDB'
                    ))
                except ValueError:
                    continue
    
    def _parse_taxiways(self):
        """Parse taxiway data"""
        if 'TAXIWAY' not in self.raw_data:
            return
            
        current_taxiway = []
        for line in self.raw_data['TAXIWAY']:
            if line.startswith(';'):
                if current_taxiway:
                    self.taxiways.append(current_taxiway)
                    current_taxiway = []
            else:
                numbers = [float(x) for x in re.findall(r'[-+]?\d*\.\d+|\d+', line)]
                for i in range(0, len(numbers)-1, 2):
                    try:
                        current_taxiway.append(Coordinate(numbers[i], numbers[i+1]))
                    except IndexError:
                        break
        
        if current_taxiway:
            self.taxiways.append(current_taxiway)
    
    def _parse_version(self):
        """Parse version information"""
        for section in self.raw_data:
            for line in self.raw_data[section]:
                version_match = self._VERSION_PATTERN.search(line)
                if version_match:
                    self.version = version_match.group(1)
                    return
    
    def get_runway_by_number(self, rwy_number: str) -> Optional[Runway]:
        for runway in self.runways:
            if runway.number == rwy_number:
                return runway
        return None
    
    def get_frequency_by_name(self, name: str) -> Optional[Frequency]:
        for freq in self.frequencies:
            if freq.name == name:
                return freq
        return None
    
    def get_navaid_by_id(self, navaid_id: str) -> Optional[Navaid]:
        for vor in self.vors:
            if vor.id == navaid_id:
                return vor
        for ndb in self.ndbs:
            if ndb.id == navaid_id:
                return ndb
        return None
    
    def validate(self) -> Tuple[bool, List[str]]:
        errors = []
        
        if not self.runways:
            errors.append("No runways found")
        
        if not self.frequencies:
            errors.append("No frequencies found")
        
        for runway in self.runways:
            if len(runway.coordinates) < 2:
                errors.append(f"Runway {runway.number} has insufficient coordinates")
        
        return len(errors) == 0, errors
    
    def export_json(self) -> str:
        import json
        return json.dumps(self.parsed_data, indent=2, default=str)
    
    def get_data(self) -> Dict[str, Any]:
        """Return the parsed data dictionary"""
        return self.parsed_data
    
    def export_summary(self) -> str:
        summary = []
        summary.append(f"SCT File: {self.file_path}")
        summary.append(f"Version: {self.version}")
        summary.append(f"Airport: {self.metadata.get('ICAO', 'Unknown')} - {self.metadata.get('Name', 'Unknown')}")
        summary.append(f"Runways: {len(self.runways)}")
        summary.append(f"Frequencies: {len(self.frequencies)}")
        summary.append(f"VORs: {len(self.vors)}")
        summary.append(f"NDBs: {len(self.ndbs)}")
        summary.append(f"Taxiways: {len(self.taxiways)}")
        summary.append(f"Airports: {len(self.airports)}")
        summary.append(f"Fixes: {len(self.fixes)}")
        summary.append(f"ARTCC HIGH boundaries: {len(self.artcc_high_boundaries)}")
        summary.append(f"ARTCC LOW boundaries: {len(self.artcc_low_boundaries)}")
        total_high_segments = sum(len(b['segments']) for b in self.artcc_high_boundaries)
        total_low_segments = sum(len(b['segments']) for b in self.artcc_low_boundaries)
        summary.append(f"  - HIGH segments: {total_high_segments}")
        summary.append(f"  - LOW segments: {total_low_segments}")
        return '\n'.join(summary)

def parse_sct_file(file_path: str, validate: bool = True) -> Dict[str, Any]:
    parser = SCTParser(file_path)
    result = parser.parse()
    
    if validate:
        is_valid, errors = parser.validate()
        if not is_valid:
            print("Validation warnings:", errors)
    
    return result

def quick_parse(file_path: str) -> str:
    parser = SCTParser(file_path)
    parser.parse()
    return parser.export_summary()

__all__ = ['SCTParser', 'parse_sct_file', 'quick_parse', 'SCTSectionType', 'Coordinate', 'Runway', 'Frequency', 'Navaid']