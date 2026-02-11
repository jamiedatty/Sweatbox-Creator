"""
Simple airport and runway fetcher using OurAirports CSV data.
Downloads and caches airports.csv and runways.csv for lookups by ICAO.
"""
import csv
import os
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

OURAIRPORTS_RUNWAYS_URL = "https://ourairports.com/data/runways.csv"
OURAIRPORTS_AIRPORTS_URL = "https://ourairports.com/data/airports.csv"
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
CACHE_RUNWAYS_FILE = os.path.join(CACHE_DIR, 'ourairports_runways.csv')
CACHE_AIRPORTS_FILE = os.path.join(CACHE_DIR, 'ourairports_airports.csv')


def _ensure_cache_file(url: str, cache_file: str):
    """Download and cache a file from URL if not already cached."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.exists(cache_file):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
            with open(cache_file, 'wb') as f:
                f.write(data)
        except Exception as e:
            # If download fails and cache doesn't exist, return False
            if not os.path.exists(cache_file):
                return False
    return True


def _ensure_cache():
    """Ensure both airports and runways caches exist."""
    _ensure_cache_file(OURAIRPORTS_RUNWAYS_URL, CACHE_RUNWAYS_FILE)
    _ensure_cache_file(OURAIRPORTS_AIRPORTS_URL, CACHE_AIRPORTS_FILE)


def fetch_airport_coordinates(icao: str) -> Optional[Dict[str, float]]:
    """Fetch airport coordinates from OurAirports data.
    
    Returns dict with 'latitude' and 'longitude' keys, or None if not found.
    """
    icao_up = (icao or '').upper()
    try:
        if not _ensure_cache_file(OURAIRPORTS_AIRPORTS_URL, CACHE_AIRPORTS_FILE):
            return None
    except Exception:
        return None
    
    try:
        with open(CACHE_AIRPORTS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ident', '').upper() == icao_up:
                    try:
                        lat = float(row.get('latitude_deg', 0))
                        lon = float(row.get('longitude_deg', 0))
                        if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat != 0 or lon != 0):
                            return {'latitude': lat, 'longitude': lon}
                    except (ValueError, TypeError):
                        pass
    except Exception as e:
        pass
    
    return None



def fetch_runways_for_icao(icao: str) -> List[Dict[str, Optional[float]]]:
    """Return list of runways for airport ICAO.

    Each runway dict contains keys: le_lat, le_lon, he_lat, he_lon, length_ft, width_ft, surface, le_ident, he_ident
    """
    icao_up = (icao or '').upper()
    try:
        _ensure_cache()
    except Exception:
        return []

    runways = []
    try:
        with open(CACHE_RUNWAYS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('airport_ident', '').upper() == icao_up:
                    try:
                        le_lat = row.get('le_latitude_deg')
                        le_lon = row.get('le_longitude_deg')
                        he_lat = row.get('he_latitude_deg')
                        he_lon = row.get('he_longitude_deg')
                        length_ft = row.get('length_ft')
                        width_ft = row.get('width_ft')
                        surface = row.get('surface')
                        le_ident = row.get('le_ident')
                        he_ident = row.get('he_ident')

                        def to_float(x):
                            try:
                                return float(x)
                            except Exception:
                                return None

                        runways.append({
                            'le_lat': to_float(le_lat),
                            'le_lon': to_float(le_lon),
                            'he_lat': to_float(he_lat),
                            'he_lon': to_float(he_lon),
                            'length_ft': length_ft,
                            'width_ft': width_ft,
                            'surface': surface,
                            'le_ident': le_ident,
                            'he_ident': he_ident,
                        })
                    except Exception:
                        continue
    except Exception:
        return []

    return runways
