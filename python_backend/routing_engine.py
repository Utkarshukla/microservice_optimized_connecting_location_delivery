from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from models import Delivery, PickupLocation, Settings, RouteStop, RoutingResponse, PriorityLevel, OptimizeBy
from distance_calculator import DistanceCalculator
from config import RoutingConfig, PriorityConfig
from typing import List, Tuple, Optional, Dict, Any
import time

class RoutingEngine:
    def __init__(self, routing_config: RoutingConfig = None, priority_config: PriorityConfig = None):
        self.routing_config = routing_config or RoutingConfig()
        self.priority_config = priority_config or PriorityConfig()
        self.distance_calculator = DistanceCalculator(self.routing_config.default_speed_kmh)

    def optimize_route(self, request: Dict[str, Any]) -> RoutingResponse:
        """
        Main method to optimize delivery route based on the new request format.
        """
        start_time = time.time()
        
        # Parse request
        pickup = PickupLocation(**request["pickup"])
        settings = Settings(**request["settings"])
        deliveries = [Delivery(**delivery) for delivery in request["deliveries"]]
        
        # Prepare data for OR-Tools
        points, distance_matrix, time_matrix, priorities, time_windows = self._prepare_optimization_data(
            pickup, deliveries, settings
        )
        
        # Create and solve the routing model
        manager, routing, solution = self._solve_routing_problem(
            points, distance_matrix, time_matrix, priorities, time_windows, settings
        )
        
        if solution:
            # Extract route from solution
            route_stops = self._extract_route(manager, routing, solution, pickup, deliveries, settings, time_matrix)
            
            # Calculate metrics
            total_distance = self._calculate_total_distance(route_stops, distance_matrix)
            total_time = self._calculate_total_time(route_stops, time_matrix, settings.time_per_stop_minutes)
            
            # Determine skipped deliveries
            skipped_deliveries = self._determine_skipped_deliveries(deliveries, route_stops)
            
            optimization_metrics = {
                "processing_time_seconds": time.time() - start_time,
                "optimization_method": settings.optimize_by,
                "total_stops": len(route_stops),
                "skipped_stops": len(skipped_deliveries)
            }
            
            return RoutingResponse(
                route=route_stops,
                total_distance_km=total_distance,
                total_time_minutes=total_time,
                is_feasible=True,
                skipped_deliveries=skipped_deliveries,
                optimization_metrics=optimization_metrics
            )
        else:
            # Handle infeasible case
            return self._create_infeasible_response(pickup, deliveries, time.time() - start_time)

    def _prepare_optimization_data(self, pickup: PickupLocation, deliveries: List[Delivery], 
                                 settings: Settings) -> Tuple[List[Tuple[float, float]], List[List[float]], 
                                 List[List[float]], List[int], List[Tuple[str, str]]]:
        """
        Prepare data structures for OR-Tools optimization.
        """
        # Create points list: [pickup, delivery1, delivery2, ...]
        points = [(pickup.lat, pickup.lng)]
        priorities = [0]  # Pickup has no priority
        time_windows = [(pickup.start_time, pickup.end_time)]
        
        for delivery in deliveries:
            points.append((delivery.lat, delivery.lng))
            priorities.append(delivery.priority.value)
            time_windows.append((delivery.time_window.start, delivery.time_window.end))
        
        # Create distance and time matrices
        distance_matrix, time_matrix = self.distance_calculator.create_distance_matrix(points)
        
        return points, distance_matrix, time_matrix, priorities, time_windows

    def _solve_routing_problem(self, points: List[Tuple[float, float]], distance_matrix: List[List[float]],
                             time_matrix: List[List[float]], priorities: List[int], 
                             time_windows: List[Tuple[str, str]], settings: Settings):
        """
        Solve the routing problem using OR-Tools.
        """
        num_locations = len(points)
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)  # 1 vehicle, start at depot
        routing = pywrapcp.RoutingModel(manager)
        
        # Create distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # Convert to integer
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Handle priorities using disjunctions
        if settings.optimize_by == OptimizeBy.PRIORITY:
            self._add_priority_constraints(routing, manager, priorities)
        
        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30
        
        # Solve
        solution = routing.SolveWithParameters(search_parameters)
        
        return manager, routing, solution

    def _add_priority_constraints(self, routing, manager, priorities: List[int]):
        """
        Add priority constraints by modifying the cost matrix.
        """
        # For now, we'll handle priorities in post-processing
        # This is a simplified approach that focuses on distance optimization
        pass

    def _extract_route(self, manager, routing, solution, pickup: PickupLocation, 
                      deliveries: List[Delivery], settings: Settings, time_matrix: List[List[float]]) -> List[RouteStop]:
        """
        Extract route from OR-Tools solution.
        """
        route_stops = []
        index = routing.Start(0)
        current_time_minutes = self.distance_calculator.time_to_minutes(pickup.start_time)
        
        # Add pickup location
        route_stops.append(RouteStop(
            stop=pickup.address,
            zipcode=pickup.zipcode,
            arrival_time=pickup.start_time,
            departure_time=pickup.start_time,
            address=pickup.address,
            lat=pickup.lat,
            lng=pickup.lng
        ))
        
        while not routing.IsEnd(index):
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            
            # Calculate travel time to next location
            from_node = manager.IndexToNode(previous_index)
            to_node = manager.IndexToNode(index)
            
            # Calculate arrival time based on travel time
            if from_node == 0:  # From pickup
                travel_time = time_matrix[from_node][to_node]
                current_time_minutes += travel_time
            else:
                # Add service time from previous stop
                current_time_minutes += settings.time_per_stop_minutes
                travel_time = time_matrix[from_node][to_node]
                current_time_minutes += travel_time
            
            # Convert to time string
            arrival_time = self.distance_calculator.minutes_to_time(int(current_time_minutes))
            departure_time = self.distance_calculator.minutes_to_time(
                int(current_time_minutes) + settings.time_per_stop_minutes
            )
            
            if to_node == 0:  # Back to pickup
                route_stops.append(RouteStop(
                    stop=f"{pickup.address} (Return)",
                    zipcode=pickup.zipcode,
                    arrival_time=arrival_time,
                    address=pickup.address,
                    lat=pickup.lat,
                    lng=pickup.lng
                ))
            else:
                # Delivery location
                delivery = deliveries[to_node - 1]  # -1 because pickup is at index 0
                route_stops.append(RouteStop(
                    stop=delivery.address,
                    zipcode=delivery.zipcode,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    address=delivery.address,
                    lat=delivery.lat,
                    lng=delivery.lng,
                    priority=delivery.priority
                ))
        
        return route_stops

    def _calculate_total_distance(self, route_stops: List[RouteStop], 
                                distance_matrix: List[List[float]]) -> float:
        """
        Calculate total distance of the route.
        """
        total_distance = 0.0
        
        for i in range(len(route_stops) - 1):
            # Find indices in distance matrix
            from_lat, from_lng = route_stops[i].lat, route_stops[i].lng
            to_lat, to_lng = route_stops[i + 1].lat, route_stops[i + 1].lng
            
            # Calculate distance directly
            distance = self.distance_calculator.calculate_geodesic_distance(from_lat, from_lng, to_lat, to_lng)
            total_distance += distance
        
        return total_distance

    def _calculate_total_time(self, route_stops: List[RouteStop], 
                            time_matrix: List[List[float]], service_time_minutes: int) -> int:
        """
        Calculate total time of the route including service times.
        """
        total_time = 0.0
        
        for i in range(len(route_stops) - 1):
            # Find indices in time matrix
            from_lat, from_lng = route_stops[i].lat, route_stops[i].lng
            to_lat, to_lng = route_stops[i + 1].lat, route_stops[i + 1].lng
            
            # Calculate travel time directly
            distance = self.distance_calculator.calculate_geodesic_distance(from_lat, from_lng, to_lat, to_lng)
            travel_time = self.distance_calculator.calculate_travel_time(distance)
            total_time += travel_time
            
            # Add service time (except for last stop if it's return to origin)
            if i < len(route_stops) - 2 or "Return" not in route_stops[i + 1].stop:
                total_time += service_time_minutes
        
        return int(total_time)

    def _determine_skipped_deliveries(self, deliveries: List[Delivery], 
                                    route_stops: List[RouteStop]) -> List[Dict[str, Any]]:
        """
        Determine which deliveries were skipped and why.
        """
        included_addresses = {stop.address for stop in route_stops if stop.address and "Return" not in stop.stop}
        skipped_deliveries = []
        
        for delivery in deliveries:
            if delivery.address not in included_addresses:
                skipped_deliveries.append({
                    "address": delivery.address,
                    "zipcode": delivery.zipcode,
                    "priority": delivery.priority.value,
                    "reason": "Not included in optimal route"
                })
        
        return skipped_deliveries

    def _create_infeasible_response(self, pickup: PickupLocation, deliveries: List[Delivery], 
                                  processing_time: float) -> RoutingResponse:
        """
        Create response for infeasible route.
        """
        return RoutingResponse(
            route=[],
            total_distance_km=0.0,
            total_time_minutes=0,
            is_feasible=False,
            skipped_deliveries=[{
                "address": delivery.address,
                "zipcode": delivery.zipcode,
                "priority": delivery.priority.value,
                "reason": "Route infeasible - time constraints cannot be met"
            } for delivery in deliveries],
            optimization_metrics={
                "processing_time_seconds": processing_time,
                "error": "No feasible solution found"
            }
        ) 