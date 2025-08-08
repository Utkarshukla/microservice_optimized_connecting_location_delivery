from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from typing import List, Tuple, Optional
import math

class DistanceCalculator:
    def __init__(self, default_speed_kmh: float = 50.0):
        self.default_speed_kmh = default_speed_kmh
        self.geocoder = Nominatim(user_agent="delivery_routing_system")

    def calculate_geodesic_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate geodesic distance between two points using their latitude and longitude.
        Returns distance in kilometers.
        """
        point1 = (lat1, lng1)
        point2 = (lat2, lng2)
        return geodesic(point1, point2).kilometers

    def calculate_travel_time(self, distance_km: float, speed_kmh: float = None) -> float:
        """
        Calculate travel time in minutes based on distance and speed.
        """
        if speed_kmh is None:
            speed_kmh = self.default_speed_kmh
        
        if speed_kmh <= 0:
            return float('inf')
        
        time_hours = distance_km / speed_kmh
        return time_hours * 60  # Convert to minutes

    def create_distance_matrix(self, points: List[Tuple[float, float]]) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Create distance and time matrices for all points.
        Returns (distance_matrix, time_matrix) where both are 2D lists.
        """
        n = len(points)
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        time_matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lng1 = points[i]
                    lat2, lng2 = points[j]
                    distance = self.calculate_geodesic_distance(lat1, lng1, lat2, lng2)
                    travel_time = self.calculate_travel_time(distance)
                    
                    distance_matrix[i][j] = distance
                    time_matrix[i][j] = travel_time

        return distance_matrix, time_matrix

    def get_location_name(self, lat: float, lng: float) -> str:
        """
        Get location name from coordinates using reverse geocoding.
        """
        try:
            location = self.geocoder.reverse((lat, lng))
            if location:
                return location.address
            return f"Location at ({lat}, {lng})"
        except Exception:
            return f"Location at ({lat}, {lng})"

    def validate_coordinates(self, lat: float, lng: float) -> bool:
        """
        Validate if coordinates are within valid ranges.
        """
        return -90 <= lat <= 90 and -180 <= lng <= 180

    def calculate_route_metrics(self, route_points: List[Tuple[float, float]], 
                              service_times: List[float] = None) -> Tuple[float, float]:
        """
        Calculate total distance and time for a route.
        """
        if len(route_points) < 2:
            return 0.0, 0.0

        total_distance = 0.0
        total_time = 0.0

        for i in range(len(route_points) - 1):
            lat1, lng1 = route_points[i]
            lat2, lng2 = route_points[i + 1]
            
            distance = self.calculate_geodesic_distance(lat1, lng1, lat2, lng2)
            travel_time = self.calculate_travel_time(distance)
            
            total_distance += distance
            total_time += travel_time

            # Add service time if provided
            if service_times and i < len(service_times):
                total_time += service_times[i]

        return total_distance, total_time

    def time_to_minutes(self, time_str: str) -> int:
        """
        Convert time string in "HH:MM" format to minutes since midnight.
        """
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0

    def minutes_to_time(self, minutes: int) -> str:
        """
        Convert minutes since midnight to "HH:MM" format.
        """
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def is_time_window_valid(self, arrival_time_minutes: int, time_window_start: str, time_window_end: str) -> bool:
        """
        Check if arrival time falls within the specified time window.
        """
        start_minutes = self.time_to_minutes(time_window_start)
        end_minutes = self.time_to_minutes(time_window_end)
        
        # Handle time windows that span midnight
        if end_minutes < start_minutes:
            return arrival_time_minutes >= start_minutes or arrival_time_minutes <= end_minutes
        else:
            return start_minutes <= arrival_time_minutes <= end_minutes 