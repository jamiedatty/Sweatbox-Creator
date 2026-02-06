import math

class RunwayCalculator:
    @staticmethod
    def calculate_extended_centerline(runway, extension_nm=10):
        """
        Calculate extended centerline coordinates for a runway
        runway: Runway object from SCT parser or dict with 'coordinates'
        extension_nm: How many nautical miles to extend
        Returns: list of (lat, lon) coordinates for extended centerline
        """
        if isinstance(runway, dict):
            if 'coordinates' not in runway or not runway['coordinates']:
                return []
            coords = runway['coordinates']
        else:
            # Runway object
            if not hasattr(runway, 'coordinates') or not runway.coordinates:
                return []
            coords = runway.coordinates
        
        if len(coords) < 2:
            return []
        
        # Get runway start and end coordinates
        if isinstance(coords[0], tuple):
            start = coords[0]
            end = coords[-1] if len(coords) > 1 else coords[0]
        else:
            # Assume Coordinate objects
            start = (coords[0].lat, coords[0].lon)
            end = (coords[-1].lat, coords[-1].lon)
        
        # Calculate bearing from start to end
        bearing = RunwayCalculator.calculate_bearing(
            start[0], start[1],
            end[0], end[1]
        )
        
        # Calculate extended point
        extended = RunwayCalculator.destination_point(
            end[0], end[1],
            bearing,
            extension_nm * 1852  # Convert NM to meters
        )
        
        return [start, end, extended]
    
    @staticmethod
    def calculate_bearing(lat1, lon1, lat2, lon2):
        """
        Calculate bearing from point 1 to point 2 in degrees
        """
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        bearing = (initial_bearing + 360) % 360
        
        return bearing
    
    @staticmethod
    def destination_point(lat, lon, bearing, distance):
        """
        Calculate destination point given start point, bearing and distance
        lat, lon: start point in degrees
        bearing: in degrees
        distance: in meters
        Returns: (lat, lon) of destination point
        """
        R = 6371000  # Earth's radius in meters
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        lat2 = math.asin(
            math.sin(lat_rad) * math.cos(distance / R) +
            math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad)
        )
        
        lon2 = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
            math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat2)
        )
        
        return (math.degrees(lat2), math.degrees(lon2))
    
    @staticmethod
    def get_ils_coordinates(runway, ils_frequency=None):
        """
        Calculate ILS localizer and glideslope coordinates
        Returns: dict with localizer and glideslope coordinates
        """
        if isinstance(runway, dict):
            if 'coordinates' not in runway or len(runway['coordinates']) < 2:
                return {}
            coords = runway['coordinates']
        else:
            if not hasattr(runway, 'coordinates') or len(runway.coordinates) < 2:
                return {}
            coords = runway.coordinates
        
        if isinstance(coords[0], tuple):
            start = coords[0]
            end = coords[-1]
        else:
            start = (coords[0].lat, coords[0].lon)
            end = (coords[-1].lat, coords[-1].lon)
        
        # Calculate localizer position (typically at runway threshold)
        threshold_lat = end[0]
        threshold_lon = end[1]
        
        # Calculate glideslope position (typically 1000ft from threshold)
        bearing = RunwayCalculator.calculate_bearing(
            start[0], start[1],
            end[0], end[1]
        )
        
        # Glideslope is typically about 300m from threshold
        gs_distance = 300  # meters
        gs_point = RunwayCalculator.destination_point(
            threshold_lat, threshold_lon,
            bearing - 180,  # Opposite direction
            gs_distance
        )
        
        return {
            'localizer': (threshold_lat, threshold_lon),
            'glideslope': gs_point,
            'frequency': ils_frequency or (runway.ils if hasattr(runway, 'ils') else None)
        }