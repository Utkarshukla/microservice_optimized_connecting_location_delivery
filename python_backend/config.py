from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class RoutingConfig(BaseModel):
    max_travel_time_hours: float = 4.0
    default_speed_kmh: float = 50.0
    buffer_time_minutes: float = 15.0
    max_route_distance_km: float = 200.0
    default_service_time_minutes: float = 10.0

class PriorityConfig(BaseModel):
    high_priority_weight: float = 1000.0
    medium_priority_weight: float = 100.0
    low_priority_weight: float = 1.0
    penalty_for_missing_high_priority: float = 10000.0

class APIConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: list = ["*"]
    title: str = "Delivery Route Optimization API"
    version: str = "1.0.0"

def get_routing_config() -> RoutingConfig:
    return RoutingConfig(
        max_travel_time_hours=float(os.getenv("MAX_TRAVEL_TIME_HOURS", "4.0")),
        default_speed_kmh=float(os.getenv("DEFAULT_SPEED_KMH", "50.0")),
        buffer_time_minutes=float(os.getenv("BUFFER_TIME_MINUTES", "15.0")),
        max_route_distance_km=float(os.getenv("MAX_ROUTE_DISTANCE_KM", "200.0")),
        default_service_time_minutes=float(os.getenv("DEFAULT_SERVICE_TIME_MINUTES", "10.0"))
    )

def get_priority_config() -> PriorityConfig:
    return PriorityConfig(
        high_priority_weight=float(os.getenv("HIGH_PRIORITY_WEIGHT", "1000.0")),
        medium_priority_weight=float(os.getenv("MEDIUM_PRIORITY_WEIGHT", "100.0")),
        low_priority_weight=float(os.getenv("LOW_PRIORITY_WEIGHT", "1.0")),
        penalty_for_missing_high_priority=float(os.getenv("PENALTY_MISSING_HIGH_PRIORITY", "10000.0"))
    )

def get_api_config() -> APIConfig:
    return APIConfig(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        debug=os.getenv("API_DEBUG", "true").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        title=os.getenv("API_TITLE", "Delivery Route Optimization API"),
        version=os.getenv("API_VERSION", "1.0.0")
    )

DEFAULT_ROUTING_CONFIG = get_routing_config()
DEFAULT_PRIORITY_CONFIG = get_priority_config()
DEFAULT_API_CONFIG = get_api_config() 