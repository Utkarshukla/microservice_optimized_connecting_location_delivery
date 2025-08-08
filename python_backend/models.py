from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import time

class PriorityLevel(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class OptimizeBy(str, Enum):
    DISTANCE = "distance"
    TIME = "time"
    PRIORITY = "priority"

class TimeWindow(BaseModel):
    start: str  # Format: "HH:MM"
    end: str    # Format: "HH:MM"

class PickupLocation(BaseModel):
    address: str
    zipcode: str
    lat: float
    lng: float
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"

class Settings(BaseModel):
    return_to_origin: bool = True
    time_per_stop_minutes: int = 10
    vehicle_speed_kmph: float = 40.0
    optimize_by: OptimizeBy = OptimizeBy.PRIORITY

class Delivery(BaseModel):
    address: str
    zipcode: str
    lat: float
    lng: float
    priority: PriorityLevel
    time_window: TimeWindow

class RoutingRequest(BaseModel):
    pickup: PickupLocation
    settings: Settings
    deliveries: List[Delivery]

class RouteStop(BaseModel):
    stop: str
    zipcode: str
    arrival_time: str
    departure_time: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    priority: Optional[PriorityLevel] = None

class RoutingResponse(BaseModel):
    route: List[RouteStop]
    total_distance_km: float
    total_time_minutes: int
    is_feasible: bool = True
    skipped_deliveries: List[Dict[str, Any]] = []
    optimization_metrics: Dict[str, Any] = {}

# Legacy models for backward compatibility
class DeliveryPoint(BaseModel):
    id: str
    latitude: float
    longitude: float
    priority: PriorityLevel
    name: Optional[str] = None
    estimated_service_time_minutes: float = 0.0

class OriginPoint(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None

class RoutingResult(BaseModel):
    route: List[RouteStop]
    total_distance_km: float
    total_time_minutes: int
    is_feasible: bool
    skipped_points: List[Dict[str, Any]] = []
    optimization_metrics: Dict[str, Any] = {}

class DistanceMatrixRequest(BaseModel):
    points: List[Dict[str, float]]  # List of {lat, lng} dictionaries

class DistanceMatrixResponse(BaseModel):
    distances: List[List[float]]
    times: List[List[float]]
    points: List[Dict[str, float]] 