#!/usr/bin/env python3
"""
Airport Layout Fetcher - Fetches detailed airport ground layouts from various online sources
Supports multiple databases and formats for comprehensive airport data.
"""

import requests
import json
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import urllib.parse

class AirportLayoutFetcher:
    """Fetches airport layout data from multiple online sources"""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # API endpoints and configurations
        self.apis = {
            'ourairports': {
                'runways': "https://ourairports.com/data/runways.csv",
                'airports': "https://ourairports.com/data/airports.csv",
                'cache_hours': 24
            },
            'openstreetmap': {
                'overpass': "https://overpass-api.de/api/interpreter",
                'cache_hours': 168  # 1 week
            },
            'faa': {
                'diagrams': "https://nfdc.faa.gov/webContent/28DaySub/28DaySubscription_Effective_2024-01-18.zip",
                'cache_hours': 168
            }
        }

    def get_airport_layout(self, icao: str) -> Dict[str, Any]:
        """
        Get comprehensive airport layout for given ICAO code.
        Returns dict with runways, taxiways, aprons, gates, etc.
        """
        icao = icao.upper().strip()

        # Try cache first
        cached = self._load_from_cache(icao)
        if cached:
            return cached

        layout = {
            'icao': icao,
            'runways': [],
            'taxiways': [],
            'aprons': [],
            'gates': [],
            'sources': [],
            'timestamp': time.time()
        }

        # Try multiple sources
        sources_tried = []

        # 1. OurAirports (runway data)
        try:
            runways = self._fetch_ourairports_runways(icao)
            if runways:
                layout['runways'].extend(runways)
                layout['sources'].append('ourairports')
                sources_tried.append('ourairports')
        except Exception as e:
            print(f"Error fetching from OurAirports: {e}")

        # 2. OpenStreetMap (detailed layout)
        try:
            osm_data = self._fetch_openstreetmap_layout(icao)
            if osm_data:
                layout.update(osm_data)
                layout['sources'].append('openstreetmap')
                sources_tried.append('openstreetmap')
        except Exception as e:
            print(f"Error fetching from OpenStreetMap: {e}")

        # 3. FAA Airport Diagrams (if US airport)
        if icao.startswith(('K', 'P')):  # US airports
            try:
                faa_data = self._fetch_faa_layout(icao)
                if faa_data:
                    layout.update(faa_data)
                    layout['sources'].append('faa')
                    sources_tried.append('faa')
            except Exception as e:
                print(f"Error fetching from FAA: {e}")

        # Cache the result
        if sources_tried:
            self._save_to_cache(icao, layout)

        return layout

    def _fetch_ourairports_runways(self, icao: str) -> List[Dict]:
        """Fetch runway data from OurAirports"""
        runways = []

        # Ensure cache file exists
        cache_file = self.cache_dir / "ourairports_runways.csv"
        if not cache_file.exists() or self._is_cache_stale(cache_file, self.apis['ourairports']['cache_hours']):
            self._download_file(self.apis['ourairports']['runways'], cache_file)

        if not cache_file.exists():
            return runways

        # Parse CSV
        import csv
        with open(cache_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('airport_ident', '').upper() == icao:
                    runway = {
                        'number': f"{row.get('le_ident', '')}/{row.get('he_ident', '')}",
                        'length_ft': int(float(row.get('length_ft', 0))),
                        'width_ft': int(float(row.get('width_ft', 0))),
                        'surface': row.get('surface', ''),
                        'le_lat': float(row.get('le_latitude_deg', 0)) if row.get('le_latitude_deg') else None,
                        'le_lon': float(row.get('le_longitude_deg', 0)) if row.get('le_longitude_deg') else None,
                        'he_lat': float(row.get('he_latitude_deg', 0)) if row.get('he_latitude_deg') else None,
                        'he_lon': float(row.get('he_longitude_deg', 0)) if row.get('he_longitude_deg') else None,
                        'le_heading': float(row.get('le_heading_degT', 0)) if row.get('le_heading_degT') else None,
                        'he_heading': float(row.get('he_heading_degT', 0)) if row.get('he_heading_degT') else None,
                    }
                    runways.append(runway)

        return runways

    def _fetch_openstreetmap_layout(self, icao: str) -> Dict[str, Any]:
        """Fetch detailed layout from OpenStreetMap using Overpass API"""
        # First get airport location
        airport_coords = self._get_airport_coords_from_ourairports(icao)
        if not airport_coords:
            return {}

        lat, lon = airport_coords

        # Query for airport features within reasonable bounds
        # Use a 5km radius around airport center
        radius = 5000  # meters

        overpass_query = f"""
        [out:json][timeout:25];
        (
          // Airport runways
          way["aeroway"="runway"](around:{radius},{lat},{lon});
          // Taxiways
          way["aeroway"="taxiway"](around:{radius},{lat},{lon});
          // Aprons
          way["aeroway"="apron"](around:{radius},{lat},{lon});
          // Aircraft stands/gates
          node["aeroway"="gate"](around:{radius},{lat},{lon});
          // Airport buildings
          way["aeroway"="terminal"](around:{radius},{lat},{lon});
          way["aeroway"="hangar"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """

        try:
            response = requests.post(
                self.apis['openstreetmap']['overpass'],
                data={'data': overpass_query},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                layout = {
                    'taxiways': [],
                    'aprons': [],
                    'gates': [],
                    'buildings': []
                }

                # Process elements
                ways = {}
                nodes = {}

                for element in data.get('elements', []):
                    if element['type'] == 'node':
                        nodes[element['id']] = (element['lat'], element['lon'])
                    elif element['type'] == 'way':
                        coords = []
                        for node_id in element.get('nodes', []):
                            if node_id in nodes:
                                coords.append(nodes[node_id])
                        ways[element['id']] = coords

                        # Categorize by tags
                        tags = element.get('tags', {})
                        aeroway = tags.get('aeroway')

                        if aeroway == 'taxiway' and len(coords) >= 2:
                            layout['taxiways'].append({
                                'name': tags.get('ref', ''),
                                'coordinates': coords
                            })
                        elif aeroway == 'apron' and len(coords) >= 3:
                            layout['aprons'].append({
                                'name': tags.get('ref', ''),
                                'coordinates': coords
                            })

                # Process gates
                for element in data.get('elements', []):
                    if element['type'] == 'node':
                        tags = element.get('tags', {})
                        if tags.get('aeroway') == 'gate':
                            layout['gates'].append({
                                'name': tags.get('ref', ''),
                                'lat': element['lat'],
                                'lon': element['lon']
                            })

                return layout

        except Exception as e:
            print(f"OSM fetch error: {e}")

        return {}

    def _fetch_faa_layout(self, icao: str) -> Dict[str, Any]:
        """Fetch FAA airport diagram data"""
        # FAA provides airport diagrams but they're PDFs
        # This is a placeholder for future PDF parsing implementation
        # For now, return empty dict
        return {}

    def _get_airport_coords_from_ourairports(self, icao: str) -> Optional[Tuple[float, float]]:
        """Get airport coordinates from OurAirports cache"""
        cache_file = self.cache_dir / "ourairports_airports.csv"
        if not cache_file.exists():
            return None

        import csv
        with open(cache_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ident', '').upper() == icao:
                    try:
                        lat = float(row.get('latitude_deg', 0))
                        lon = float(row.get('longitude_deg', 0))
                        return (lat, lon)
                    except (ValueError, TypeError):
                        pass
        return None

    def _load_from_cache(self, icao: str) -> Optional[Dict]:
        """Load airport layout from cache"""
        cache_file = self.cache_dir / f"airport_layout_{icao.lower()}.json"
        if not cache_file.exists():
            return None

        # Check if cache is stale (older than 24 hours)
        if self._is_cache_stale(cache_file, 24):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_to_cache(self, icao: str, layout: Dict):
        """Save airport layout to cache"""
        cache_file = self.cache_dir / f"airport_layout_{icao.lower()}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(layout, f, indent=2)
        except Exception as e:
            print(f"Error caching layout for {icao}: {e}")

    def _download_file(self, url: str, dest_path: Path):
        """Download file from URL to destination path"""
        try:
            with requests.get(url, timeout=30, stream=True) as response:
                response.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    def _is_cache_stale(self, cache_file: Path, max_hours: int) -> bool:
        """Check if cache file is older than max_hours"""
        if not cache_file.exists():
            return True

        age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
        return age_hours > max_hours


# Convenience functions
def get_airport_layout(icao: str) -> Dict[str, Any]:
    """Get airport layout for ICAO code"""
    fetcher = AirportLayoutFetcher()
    return fetcher.get_airport_layout(icao)

def get_runways_for_airport(icao: str) -> List[Dict]:
    """Get runway data for airport"""
    layout = get_airport_layout(icao)
    return layout.get('runways', [])

if __name__ == "__main__":
    # Test with JFK
    layout = get_airport_layout("KJFK")
    print(f"Layout for KJFK: {len(layout.get('runways', []))} runways")
    print(f"Sources: {layout.get('sources', [])}")
