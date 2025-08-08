"""
Visualization utilities for the delivery routing system.
"""

import logging
import folium
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from models import PickupLocation, Delivery, RoutingResponse, RouteStop
import os

logger = logging.getLogger(__name__)

class RouteVisualizer:
    def __init__(self, distance_calculator):
        self.distance_calculator = distance_calculator
    
    def create_interactive_map(self, pickup: PickupLocation, deliveries: List[Delivery], result: RoutingResponse, filename: str):
        """Create an interactive map visualization using Folium."""
        try:
            logger.info(f"Creating interactive map: {filename}")
            
            # Calculate center point for the map
            all_lats = [pickup.lat] + [d.lat for d in deliveries]
            all_lngs = [pickup.lng] + [d.lng for d in deliveries]
            center_lat = sum(all_lats) / len(all_lats)
            center_lng = sum(all_lngs) / len(all_lngs)
            
            # Create the map
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Add pickup location
            folium.Marker(
                [pickup.lat, pickup.lng],
                popup=f"<b>Pickup: {pickup.address}</b><br>Zip: {pickup.zipcode}<br>Time: {pickup.start_time}",
                icon=folium.Icon(color='green', icon='warehouse', prefix='fa'),
                tooltip="Pickup Location"
            ).add_to(m)
            
            # Add delivery locations
            for i, delivery in enumerate(deliveries):
                folium.Marker(
                    [delivery.lat, delivery.lng],
                    popup=f"<b>Delivery {i+1}: {delivery.address}</b><br>Zip: {delivery.zipcode}<br>Priority: {delivery.priority}<br>Time Window: {delivery.time_window.start}-{delivery.time_window.end}",
                    icon=folium.Icon(color='red', icon='map-marker', prefix='fa'),
                    tooltip=f"Delivery {i+1}: {delivery.address}"
                ).add_to(m)
            
            # Draw the optimized route
            if result.route and len(result.route) > 1:
                route_coords = []
                for stop in result.route:
                    route_coords.append([stop.lat, stop.lng])
                
                # Create route line
                folium.PolyLine(
                    route_coords,
                    weight=3,
                    color='blue',
                    opacity=0.8,
                    popup=f"Optimized Route<br>Distance: {result.total_distance_km:.2f} km<br>Time: {result.total_time_minutes} min"
                ).add_to(m)
                
                # Add route markers with sequence numbers
                for i, stop in enumerate(result.route):
                    if i == 0:  # Pickup
                        icon_color = 'green'
                        icon_name = 'warehouse'
                    elif i == len(result.route) - 1 and 'Return' in stop.stop:  # Return to pickup
                        icon_color = 'darkgreen'
                        icon_name = 'home'
                    else:  # Delivery
                        icon_color = 'orange'
                        icon_name = 'map-marker'
                    
                    folium.Marker(
                        [stop.lat, stop.lng],
                        popup=f"<b>Stop {i+1}: {stop.stop}</b><br>Arrival: {stop.arrival_time}<br>Departure: {stop.departure_time or 'N/A'}<br>Zip: {stop.zipcode}",
                        icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa'),
                        tooltip=f"Stop {i+1}: {stop.stop}"
                    ).add_to(m)
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><b>Route Legend</b></p>
            <p><i class="fa fa-warehouse" style="color:green"></i> Pickup Location</p>
            <p><i class="fa fa-map-marker" style="color:red"></i> Delivery Points</p>
            <p><i class="fa fa-map-marker" style="color:orange"></i> Route Stops</p>
            <p><i class="fa fa-home" style="color:darkgreen"></i> Return to Pickup</p>
            <p><b>Blue Line:</b> Optimized Route</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Save the map
            m.save(filename)
            logger.info(f"Interactive map saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error creating interactive map: {e}")
            raise
    
    def create_route_summary_chart(self, result: RoutingResponse, filename: str):
        """Create a summary chart of the route using matplotlib."""
        try:
            logger.info(f"Creating route summary chart: {filename}")
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Distance and time summary
            labels = ['Distance (km)', 'Time (min)']
            values = [result.total_distance_km, result.total_time_minutes]
            colors = ['#2E86AB', '#A23B72']
            
            bars = ax1.bar(labels, values, color=colors, alpha=0.7)
            ax1.set_title('Route Summary', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Value')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
            
            # Route timeline
            if result.route:
                stops = [stop.stop for stop in result.route]
                times = [stop.arrival_time for stop in result.route]
                
                # Convert times to minutes for plotting
                time_minutes = []
                for time_str in times:
                    hours, minutes = map(int, time_str.split(':'))
                    time_minutes.append(hours * 60 + minutes)
                
                ax2.plot(range(len(stops)), time_minutes, 'bo-', linewidth=2, markersize=8)
                ax2.set_xlabel('Stop Number')
                ax2.set_ylabel('Arrival Time (minutes from start)')
                ax2.set_title('Route Timeline', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                
                # Add stop labels
                for i, stop in enumerate(stops):
                    ax2.annotate(stop.split(',')[0], (i, time_minutes[i]), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Route summary chart saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error creating route summary chart: {e}")
            raise
    
    def create_route_timeline(self, result: RoutingResponse, filename: str):
        """Create a timeline visualization of the route."""
        try:
            logger.info(f"Creating route timeline: {filename}")
            
            if not result.route:
                logger.warning("No route data available for timeline")
                return
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create timeline
            y_positions = list(range(len(result.route)))
            times = []
            
            for stop in result.route:
                hours, minutes = map(int, stop.arrival_time.split(':'))
                times.append(hours * 60 + minutes)  # Convert to minutes
            
            # Plot timeline
            ax.plot(times, y_positions, 'bo-', linewidth=3, markersize=10)
            
            # Add stop labels
            for i, stop in enumerate(result.route):
                ax.annotate(f"{stop.stop}\n{stop.arrival_time}", 
                           (times[i], i), xytext=(10, 0), 
                           textcoords='offset points', fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
            
            ax.set_xlabel('Time (minutes from start)', fontsize=12)
            ax.set_ylabel('Stop Number', fontsize=12)
            ax.set_title('Route Timeline', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis to show time
            ax.set_xticks(times)
            ax.set_xticklabels([stop.arrival_time for stop in result.route], rotation=45)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Route timeline saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error creating route timeline: {e}")
            raise
    
    def print_route_debug_info(self, result: RoutingResponse):
        """Print debug information about the route."""
        try:
            logger.info("=== ROUTE DEBUG INFO ===")
            logger.info(f"Route feasible: {result.is_feasible}")
            logger.info(f"Total distance: {result.total_distance_km:.2f} km")
            logger.info(f"Total time: {result.total_time_minutes} minutes")
            logger.info(f"Number of stops: {len(result.route)}")
            logger.info(f"Skipped deliveries: {len(result.skipped_deliveries)}")
            
            if result.route:
                logger.info("Route stops:")
                for i, stop in enumerate(result.route):
                    logger.info(f"  {i+1}. {stop.stop} ({stop.zipcode}) - Arrival: {stop.arrival_time}")
            
            if result.skipped_deliveries:
                logger.info("Skipped deliveries:")
                for delivery in result.skipped_deliveries:
                    logger.info(f"  - {delivery}")
            
            logger.info("=== END DEBUG INFO ===")
        except Exception as e:
            logger.error(f"Error printing debug info: {e}") 