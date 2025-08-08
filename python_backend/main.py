"""
FastAPI main application for the delivery routing system.
"""
import time
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from models import (
    RoutingRequest, RoutingResponse, DistanceMatrixRequest, DistanceMatrixResponse,
    Delivery, PickupLocation, Settings, RouteStop, PriorityLevel
)
from routing_engine import RoutingEngine
from distance_calculator import DistanceCalculator
from visualization import RouteVisualizer
from config import get_routing_config, get_priority_config, DEFAULT_API_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=DEFAULT_API_CONFIG.title,
    version=DEFAULT_API_CONFIG.version,
    description="A region-based delivery routing system with priority-based optimization"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
routing_config = get_routing_config()
priority_config = get_priority_config()
routing_engine = RoutingEngine(routing_config, priority_config)
distance_calculator = DistanceCalculator(routing_config.default_speed_kmh)
visualizer = RouteVisualizer(distance_calculator)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Delivery Routing API",
        "version": DEFAULT_API_CONFIG.version,
        "description": "Region-based delivery routing with priority optimization",
        "endpoints": {
            "/optimize-route": "POST - Optimize delivery route",
            "/calculate-distance-matrix": "POST - Calculate distance/time matrix",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "max_travel_time_hours": routing_config.max_travel_time_hours,
            "default_speed_kmh": routing_config.default_speed_kmh,
            "high_priority_weight": priority_config.high_priority_weight
        }
    }

@app.post("/optimize-route", response_model=RoutingResponse)
async def optimize_route(request: RoutingRequest, background_tasks: BackgroundTasks):
    """
    Optimize delivery route considering priorities and constraints.
    
    This endpoint takes a pickup location, settings, and delivery points with priorities 
    and optimizes the route to maximize high priority deliveries while staying within time constraints.
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not request.deliveries:
            raise HTTPException(status_code=400, detail="At least one delivery point is required")
        
        # Validate coordinates
        if not distance_calculator.validate_coordinates(request.pickup.lat, request.pickup.lng):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid coordinates for pickup: {request.pickup.lat}, {request.pickup.lng}"
            )
        
        for delivery in request.deliveries:
            if not distance_calculator.validate_coordinates(delivery.lat, delivery.lng):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid coordinates for delivery {delivery.address}: {delivery.lat}, {delivery.lng}"
                )
        
        # Convert request to dictionary for routing engine
        request_dict = request.dict()
        
        # Optimize route
        result = routing_engine.optimize_route(request_dict)
        
        processing_time = time.time() - start_time
        
        # Create visualizations in background if route is feasible
        if result.is_feasible:
            background_tasks.add_task(
                create_visualizations,
                request.pickup,
                request.deliveries,
                result
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        processing_time = time.time() - start_time
        return RoutingResponse(
            route=[],
            total_distance_km=0.0,
            total_time_minutes=0,
            is_feasible=False,
            skipped_deliveries=[{"error": f"Internal server error: {str(e)}"}]
        )

@app.post("/calculate-distance-matrix", response_model=DistanceMatrixResponse)
async def calculate_distance_matrix(request: DistanceMatrixRequest):
    """
    Calculate distance and time matrix for a set of points.
    
    This endpoint calculates the pairwise distances and travel times between
    all points in the provided list.
    """
    try:
        # Validate input
        if len(request.points) < 2:
            raise HTTPException(status_code=400, detail="At least 2 points are required")
        
        # Extract coordinates
        coordinates = []
        for point in request.points:
            if 'latitude' not in point or 'longitude' not in point:
                raise HTTPException(status_code=400, detail="Each point must have latitude and longitude")
            
            lat, lng = point['latitude'], point['longitude']
            if not distance_calculator.validate_coordinates(lat, lng):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid coordinates: {lat}, {lng}"
                )
            coordinates.append((lat, lng))
        
        # Calculate matrices
        if request.use_geodesic:
            distance_matrix, time_matrix = distance_calculator.create_distance_matrix(coordinates)
        else:
            # For future implementation with external APIs
            distance_matrix, time_matrix = distance_calculator.create_distance_matrix(coordinates)
        
        return DistanceMatrixResponse(
            distances=distance_matrix,
            times=time_matrix,
            points=request.points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating distance matrix: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/visualizations/{filename}")
async def get_visualization(filename: str):
    """
    Get generated visualization files.
    
    Available files:
    - route_map.html: Interactive map
    - route_summary.png: Summary chart
    - route_timeline.png: Timeline chart
    """
    try:
        return FileResponse(filename, media_type='application/octet-stream')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Visualization file {filename} not found")

@app.post("/generate-visualizations")
async def generate_visualizations(request: RoutingRequest):
    """
    Generate visualizations for a route optimization request.
    
    Returns links to the generated visualization files:
    - Interactive map (HTML)
    - Route summary chart (PNG)
    - Route timeline (PNG)
    """
    try:
        # Convert request to dictionary for routing engine
        request_dict = request.dict()
        
        # Optimize route
        result = routing_engine.optimize_route(request_dict)
        
        # Create visualizations
        if result.is_feasible:
            create_visualizations(request.pickup, request.deliveries, result)
            
            base_url = "http://127.0.0.1:8000/visualizations"
            return {
                "success": True,
                "route_result": result,
                "visualizations": {
                    "interactive_map": f"{base_url}/route_map.html",
                    "summary_chart": f"{base_url}/route_summary.png",
                    "timeline": f"{base_url}/route_timeline.png"
                },
                "message": "Visualizations generated successfully. Open the HTML file in your browser to view the interactive map."
            }
        else:
            return {
                "success": False,
                "route_result": result,
                "message": "Route is not feasible. No visualizations generated."
            }
            
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
        return {
            "success": False,
            "error_message": str(e)
        }

@app.post("/debug-route")
async def debug_route(request: RoutingRequest):
    """
    Debug endpoint that provides detailed information about route optimization.
    
    This endpoint returns the same optimization result but with additional
    debug information printed to the console.
    """
    try:
        # Convert request to dictionary for routing engine
        request_dict = request.dict()
        
        # Optimize route
        result = routing_engine.optimize_route(request_dict)
        
        # Print debug information
        visualizer.print_route_debug_info(result)
        
        # Create visualizations
        if result.is_feasible:
            create_visualizations(request.pickup, request.deliveries, result)
        
        return {
            "success": True,
            "result": result,
            "debug_info": "Check console output for detailed debug information"
        }
        
    except Exception as e:
        logger.error(f"Error in debug route: {e}")
        return {
            "success": False,
            "error_message": str(e)
        }

def create_visualizations(pickup: PickupLocation, deliveries: List[Delivery], result):
    """Create visualization files for the route."""
    try:
        # Create interactive map
        visualizer.create_interactive_map(pickup, deliveries, result, "route_map.html")
        
        # Create summary chart
        visualizer.create_route_summary_chart(result, "route_summary.png")
        
        # Create timeline
        if result.is_feasible:
            visualizer.create_route_timeline(result, "route_timeline.png")
        
        logger.info("Visualizations created successfully")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")

# Example data endpoints for testing
@app.get("/example-data")
async def get_example_data():
    """Get example data for testing the API."""
    return {
        "pickup": {
            "address": "Warehouse, Mumbai",
            "zipcode": "400001",
            "lat": 18.9356,
            "lng": 72.8376,
            "start_time": "09:00",
            "end_time": "18:00"
        },
        "settings": {
            "return_to_origin": True,
            "time_per_stop_minutes": 10,
            "vehicle_speed_kmph": 40.0,
            "optimize_by": "priority"
        },
        "deliveries": [
            {
                "address": "Client A",
                "zipcode": "400020",
                "lat": 18.9447,
                "lng": 72.8235,
                "priority": 1,
                "time_window": {
                    "start": "10:00",
                    "end": "13:00"
                }
            },
            {
                "address": "Client B",
                "zipcode": "400028",
                "lat": 18.9894,
                "lng": 72.8295,
                "priority": 2,
                "time_window": {
                    "start": "12:00",
                    "end": "17:00"
                }
            },
            {
                "address": "Client C",
                "zipcode": "400033",
                "lat": 19.0158,
                "lng": 72.8438,
                "priority": 3,
                "time_window": {
                    "start": "09:00",
                    "end": "11:30"
                }
            }
        ]
    }

@app.get("/config")
async def get_config():
    """Get current configuration settings."""
    return {
        "routing_config": routing_config.dict(),
        "priority_config": priority_config.dict(),
        "api_config": DEFAULT_API_CONFIG.dict()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=DEFAULT_API_CONFIG.host,
        port=DEFAULT_API_CONFIG.port,
        reload=DEFAULT_API_CONFIG.debug
    ) 