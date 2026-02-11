# sct_parser_simple.py
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
            'runways': [{
                'number': r.number,
                'heading': r.heading,
                'length': r.length,
                'width': r.width,
                'surface': r.surface,
                'ils': r.ils,
                'coordinates': [(c.lat, c.lon) for c in r.coordinates]  # Convert to tuples
            } for r in self.runways],
            'frequencies': [f.__dict__ for f in self.frequencies],
            'VOR': [{'latitude': v.coord.lat, 'longitude': v.coord.lon, 'name': v.name, 'id': v.id} for v in self.vors],
            'NDB': [{'latitude': n.coord.lat, 'longitude': n.coord.lon, 'name': n.name, 'id': n.id} for n in self.ndbs],
            'taxiways': self.taxiways,
            'airports': self.airports,
            'fixes': self.fixes,
            'ARTCC_HIGH': self.artcc_high_boundaries,
            'ARTCC_LOW': self.artcc_low_boundaries,
            'ARTCC': self.artcc_high_boundaries + self.artcc_low_boundaries,
            'version': self.version,
            'raw_sections': self.raw_data
        }
        
        print(f"DEBUG PARSER: Parsed {len(self.airports)} airports, {len(self.fixes)} fixes")
        print(f"DEBUG PARSER: ARTCC HIGH: {len(self.artcc_high_boundaries)} boundaries")
        print(f"DEBUG PARSER: ARTCC LOW: {len(self.artcc_low_boundaries)} boundaries")
        print(f"DEBUG PARSER: Total segments - HIGH: {sum(len(b['segments']) for b in self.artcc_high_boundaries)}")
        print(f"DEBUG PARSER: Total segments - LOW: {sum(len(b['segments']) for b in self.artcc_low_boundaries)}")
        
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
        """Parse ARTCC boundaries - handles coordinates on same line as name"""
        boundaries = []
        current_boundary = None
        current_path = []
        
        print(f"\n=== PARSING ARTCC: {len(lines)} lines ===")
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains coordinates (S/N followed by numbers)
            has_coords = bool(re.search(r'[SN]\d{3}\.\d{2}\.\d{2}\.\d{3}', line))
            
            if idx < 5:
                print(f"Line {idx}: '{line[:80]}'")
                print(f"  Has coords: {has_coords}")
            
            if has_coords:
                # This line has coordinates - extract name and coords
                # Format: NAME    S037.00.00.000 E022.00.00.000 S037.00.00.000 E015.00.00.000
                
                # Split on coordinate pattern
                parts = re.split(r'([SN]\d{3}\.\d{2}\.\d{2}\.\d{3}\s+[EW]\d{3}\.\d{2}\.\d{2}\.\d{3})', line)
                
                # First part is the name (before coordinates)
                name = parts[0].strip() if parts else "UNNAMED"
                
                # Filter out _FSS and _CTR boundaries
                if '_FSS' in name.upper() or '_CTR' in name.upper():
                    if idx < 5:
                        print(f"  Skipping FSS/CTR boundary: {name[:40]}")
                    continue
                
                # End previous boundary if exists
                if current_boundary and current_boundary['name'] != name:
                    self._add_path_to_boundary(current_boundary, current_path)
                    boundaries.append(current_boundary)
                    print(f"✓ Boundary '{current_boundary['name'][:30]}': {len(current_boundary['segments'])} segs")
                    current_boundary = None
                    current_path = []
                
                # Start new boundary if needed
                if not current_boundary:
                    current_boundary = {'name': name, 'segments': []}
                    print(f"✓ New boundary: '{name[:40]}'")
                
                # Extract all coordinate pairs from this line
                coord_pattern = r'([SN])(\d{3})\.(\d{2})\.(\d{2})\.(\d{3})\s+([EW])(\d{3})\.(\d{2})\.(\d{2})\.(\d{3})'
                coord_matches = list(re.finditer(coord_pattern, line))
                
                if idx < 5:
                    print(f"  Found {len(coord_matches)} coordinate pairs")
                
                # Parse coordinates in pairs (start, end)
                for i in range(0, len(coord_matches), 2):
                    if i + 1 >= len(coord_matches):
                        break
                    
                    # Parse start coordinate
                    m1 = coord_matches[i]
                    lat_dir, lat_d, lat_m, lat_s, lat_ms = m1.groups()[:5]
                    lon_dir, lon_d, lon_m, lon_s, lon_ms = m1.groups()[5:]
                    
                    lat1 = float(lat_d) + float(lat_m)/60 + (float(lat_s) + float(lat_ms)/1000)/3600
                    if lat_dir == 'S':
                        lat1 = -lat1
                    lon1 = float(lon_d) + float(lon_m)/60 + (float(lon_s) + float(lon_ms)/1000)/3600
                    if lon_dir == 'W':
                        lon1 = -lon1
                    
                    # Parse end coordinate
                    m2 = coord_matches[i + 1]
                    lat_dir, lat_d, lat_m, lat_s, lat_ms = m2.groups()[:5]
                    lon_dir, lon_d, lon_m, lon_s, lon_ms = m2.groups()[5:]
                    
                    lat2 = float(lat_d) + float(lat_m)/60 + (float(lat_s) + float(lat_ms)/1000)/3600
                    if lat_dir == 'S':
                        lat2 = -lat2
                    lon2 = float(lon_d) + float(lon_m)/60 + (float(lon_s) + float(lon_ms)/1000)/3600
                    if lon_dir == 'W':
                        lon2 = -lon2
                    
                    start_coord = (lat1, lon1)
                    end_coord = (lat2, lon2)
                    
                    if idx < 5 and i == 0:
                        print(f"  Coord pair: {start_coord} → {end_coord}")
                    
                    # Add to path
                    if not current_path:
                        current_path = [start_coord, end_coord]
                    elif self._coords_equal(current_path[-1], start_coord):
                        current_path.append(end_coord)
                    else:
                        self._add_path_to_boundary(current_boundary, current_path)
                        current_path = [start_coord, end_coord]
            else:
                # Line without coordinates - might be continuation or new boundary
                if current_boundary:
                    # Save current boundary
                    self._add_path_to_boundary(current_boundary, current_path)
                    boundaries.append(current_boundary)
                    print(f"✓ Boundary '{current_boundary['name'][:30]}': {len(current_boundary['segments'])} segs")
                    current_boundary = None
                    current_path = []
        
        # Handle last boundary
        if current_boundary:
            self._add_path_to_boundary(current_boundary, current_path)
            boundaries.append(current_boundary)
            print(f"✓ Last boundary '{current_boundary['name'][:30]}': {len(current_boundary['segments'])} segs")
        
        total = sum(len(b['segments']) for b in boundaries)
        print(f"=== RESULT: {len(boundaries)} boundaries, {total} segments ===\n")
        
        return boundaries
    
    def _coords_equal(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> bool:
        """Check if two coordinates are approximately equal"""
        return (abs(coord1[0] - coord2[0]) < 0.0001 and 
                abs(coord1[1] - coord2[1]) < 0.0001)
    
    def _add_path_to_boundary(self, boundary: Dict, path: List[Tuple[float, float]]):
        """Convert a continuous path into segments and add to boundary"""
        if len(path) < 2:
            return
        
        # Create segments from the path
        for i in range(len(path) - 1):
            boundary['segments'].append({
                'start': {'lat': path[i][0], 'lon': path[i][1]},
                'end': {'lat': path[i + 1][0], 'lon': path[i + 1][1]}
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
    
    def _parse_dms_coordinate(self, dms_str: str) -> Optional[float]:
        """Parse DMS (Degrees Minutes Seconds) format coordinate.
        
        Examples:
        - N025.17.27.520 -> latitude 25.290866...
        - E051.35.23.071 -> longitude 51.589741...
        """
        if not dms_str or len(dms_str) < 4:
            return None
        
        try:
            # First character is N/S/E/W
            direction = dms_str[0].upper()
            dms_value = dms_str[1:]  # Remove direction prefix
            
            # Split by dots
            parts = dms_value.split('.')
            if len(parts) < 3:
                return None
            
            degrees = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2]) if len(parts) > 2 else 0
            
            # Convert to decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply direction (S and W are negative)
            if direction in ['S', 'W']:
                decimal = -decimal
            
            return decimal
        except (ValueError, IndexError):
            return None
    
    def _parse_dms_coordinate_pair(self, lat_str: str, lon_str: str) -> Optional[tuple]:
        """Parse a pair of DMS coordinates and return (lat, lon) or None."""
        lat = self._parse_dms_coordinate(lat_str)
        lon = self._parse_dms_coordinate(lon_str)
        
        if lat is not None and lon is not None:
            return (lat, lon)
        return None
    
    def _parse_decimal_coordinate(self, coord_str: str) -> Optional[float]:
        """Parse decimal coordinate (simple float)."""
        try:
            val = float(coord_str)
            if -180 <= val <= 180:  # Basic range check
                return val
        except ValueError:
            pass
        return None
    
    def _parse_runways(self):
        """Parse runway data - handles both decimal and DMS formats"""
        if 'RUNWAY' not in self.raw_data:
            print("DEBUG: No RUNWAY section found in SCT file")
            return
        
        print(f"\nDEBUG: Parsing {len(self.raw_data['RUNWAY'])} runway lines")
        
        for idx, line in enumerate(self.raw_data['RUNWAY']):
            if idx < 3:
                print(f"  Runway line {idx}: '{line[:80]}'")
            
            parts = line.split()
            if idx < 3:
                print(f"    Parts: {len(parts)} -> {parts[:6]}")
            
            # Try to handle DMS format first (has N/E/S/W coordinates)
            # Format: RWY_NUM1 RWY_NUM2 HDG1 HDG2 LAT LON LAT LON AIRPORT ...
            dms_coords = [p for p in parts if p and (p[0] in 'NSEW')]
            
            if len(dms_coords) >= 2:  # Can parse DMS format
                try:
                    # DMS format: runway_num1 runway_num2 heading1 heading2 lat lon lat lon airport_id
                    rwy_num1 = parts[0] if parts else "???"
                    rwy_num2 = parts[1] if len(parts) > 1 else None
                    heading1 = float(parts[2]) if len(parts) > 2 else 0
                    heading2 = float(parts[3]) if len(parts) > 3 else 0
                    
                    coords = []
                    # Coordinates should be right after the headings
                    for i in range(4, len(parts) - 1, 2):
                        if i < len(parts) - 1:
                            lat_str = parts[i]
                            lon_str = parts[i + 1]
                            
                            # Check if this looks like DMS coordinates
                            if lat_str and lat_str[0] in 'NS' and lon_str and lon_str[0] in 'EW':
                                coord_pair = self._parse_dms_coordinate_pair(lat_str, lon_str)
                                if coord_pair:
                                    coords.append(Coordinate(coord_pair[0], coord_pair[1]))
                    
                    if idx < 3:
                        print(f"    [OK] Parsed runway {rwy_num1}: {len(coords)} DMS coordinates")
                    
                    if len(coords) >= 2:
                        self.runways.append(Runway(
                            number=rwy_num1,
                            heading=heading1,
                            length=0,  # Not available in DMS format
                            width=0,   # Not available in DMS format
                            surface="ASPH",  # Default assumption
                            ils=None,
                            coordinates=coords
                        ))
                        
                        # Also add the reciprocal runway if it exists (16R/34L)
                        if rwy_num2:
                            self.runways.append(Runway(
                                number=rwy_num2,
                                heading=heading2,
                                length=0,
                                width=0,
                                surface="ASPH",
                                ils=None,
                                coordinates=list(reversed(coords))  # Reversed coordinates for opposite direction
                            ))
                except Exception as e:
                    if idx < 3:
                        print(f"    [ERROR] DMS parse failed: {e}")
                    continue
            
            # Fall back to standard decimal format
            elif len(parts) >= 6:
                try:
                    rwy_num = parts[0]
                    heading = float(parts[1])
                    length = int(parts[2])
                    width = int(parts[3]) if len(parts) > 3 else 100
                    surface = parts[4] if len(parts) > 4 else "ASPH"
                    
                    coords = []
                    for i in range(5, len(parts) - 1, 2):
                        try:
                            lat = float(parts[i])
                            lon = float(parts[i + 1])
                            coords.append(Coordinate(lat, lon))
                        except ValueError:
                            continue
                    
                    if idx < 3:
                        print(f"    [OK] Parsed runway {rwy_num}: {len(coords)} decimal coordinates")
                    
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
                except (ValueError, IndexError) as e:
                    if idx < 3:
                        print(f"    [ERROR] Decimal parse failed: {e}")
                    continue
        
        print(f"DEBUG: Parsed {len(self.runways)} runways total\n")
    
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