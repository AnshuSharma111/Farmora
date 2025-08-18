"""
Enhanced geolocation utilities for more accurate location-based market lookup.

This module provides functions to accurately determine the nearest district and market
based on user coordinates, focusing on improving the user experience for location-based
commodity price lookup.
"""

import math
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from collections import defaultdict

# Define paths to data files
DATA_DIR = Path(__file__).parent.parent / "data"
MARKETS_FILE = DATA_DIR / "markets_database.json"
DISTRICTS_FILE = DATA_DIR / "districts_database.json"

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the distance between two coordinates in kilometers using the Haversine formula.
    
    Args:
        coord1: First coordinate (latitude, longitude)
        coord2: Second coordinate (latitude, longitude)
        
    Returns:
        Distance in kilometers
    """
    # Try to use geopy if available
    try:
        from geopy.distance import geodesic
        return geodesic(coord1, coord2).kilometers
    except ImportError:
        # Fallback to haversine formula
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Earth's radius in kilometers
        radius = 6371.0
        
        # Calculate the distance
        distance = radius * c
        
        return distance

def get_state_from_coordinates(lat: float, lon: float) -> str:
    """
    Determine the state based on provided coordinates by checking against district database.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        State name as string
    """
    # Create districts database file if it doesn't exist (simplified version)
    if not os.path.exists(DISTRICTS_FILE):
        return "Punjab"  # Default fallback
    
    # Load district coordinates database
    try:
        with open(DISTRICTS_FILE, 'r') as f:
            districts_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return "Punjab"  # Default fallback
    
    # Find nearest district
    nearest_district = None
    min_distance = float('inf')
    
    for district_entry in districts_data:
        dist_lat = district_entry.get("latitude")
        dist_lon = district_entry.get("longitude")
        
        if not (dist_lat and dist_lon):
            continue
            
        distance = haversine_distance((lat, lon), (dist_lat, dist_lon))
        
        if distance < min_distance:
            min_distance = distance
            nearest_district = district_entry
    
    if nearest_district:
        return nearest_district.get("state", "Punjab")
    else:
        return "Punjab"

def get_nearest_district(lat: float, lon: float, state: str) -> Dict[str, Any]:
    """
    Find the nearest district in a state based on coordinates.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        state: State name to filter districts
        
    Returns:
        Dictionary with district information including name, state, coordinates and distance
    """
    # Create districts database file if it doesn't exist (simplified version)
    if not os.path.exists(DISTRICTS_FILE):
        return {"district": "Ludhiana", "state": state, "distance": 0}
    
    # Load district coordinates database
    try:
        with open(DISTRICTS_FILE, 'r') as f:
            districts_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"district": "Ludhiana", "state": state, "distance": 0}
    
    # Filter districts by state
    state_districts = [d for d in districts_data if d.get("state") == state]
    
    if not state_districts:
        return {"district": "Ludhiana", "state": state, "distance": 0}
    
    # Find nearest district in the state
    nearest_district = None
    min_distance = float('inf')
    
    for district_entry in state_districts:
        dist_lat = district_entry.get("latitude")
        dist_lon = district_entry.get("longitude")
        
        if not (dist_lat and dist_lon):
            continue
            
        distance = haversine_distance((lat, lon), (dist_lat, dist_lon))
        
        if distance < min_distance:
            min_distance = distance
            nearest_district = district_entry
    
    if nearest_district:
        return {
            "district": nearest_district.get("district"),
            "state": state,
            "latitude": nearest_district.get("latitude"),
            "longitude": nearest_district.get("longitude"),
            "distance": min_distance
        }
    else:
        return {"district": "Ludhiana", "state": state, "distance": 0}

def get_markets_in_district(district: str) -> List[str]:
    """
    Get all markets in a specific district.
    
    Args:
        district: District name
        
    Returns:
        List of market names in the district
    """
    # Create markets database file if it doesn't exist (simplified version)
    if not os.path.exists(MARKETS_FILE):
        return ["Ludhiana"]  # Default fallback
    
    # Load markets database
    try:
        with open(MARKETS_FILE, 'r') as f:
            markets_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return ["Ludhiana"]  # Default fallback
    
    # Extract markets for the specified district
    district_markets = []
    
    for market_entry in markets_data:
        if market_entry.get("district") == district:
            district_markets.append(market_entry.get("market"))
    
    return district_markets if district_markets else ["Ludhiana"]

def find_nearest_market_and_district(lat: float, lon: float) -> Dict[str, Any]:
    """
    Find the nearest market and district based on user coordinates.
    This is a comprehensive function that handles the entire location lookup process.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        Dictionary with state, district, market and distance information
    """
    # Step 1: Determine the state based on coordinates
    state = get_state_from_coordinates(lat, lon)
    
    # Step 2: Get the nearest district in that state
    district_info = get_nearest_district(lat, lon, state)
    
    # Step 3: Get available markets in the district
    markets = get_markets_in_district(district_info.get("district", "Ludhiana"))
    
    # Step 4: Return the complete location information
    return {
        "state": state,
        "district": district_info.get("district"),
        "markets": markets,
        "primary_market": markets[0] if markets else "Ludhiana",
        "distance_km": district_info.get("distance", 0)
    }

def get_alternate_markets(state: str, commodity: str) -> List[Dict[str, Any]]:
    """
    Get a list of alternative markets in the state that might have data for the specified commodity.
    
    Args:
        state: State name
        commodity: Commodity name
        
    Returns:
        List of dictionaries with market information
    """
    # This would ideally come from a database of market-commodity relationships
    # For now, we'll return some predefined markets for major states
    
    # Map of states to their major agricultural markets
    state_markets = {
        "Punjab": [
            {"district": "Ludhiana", "market": "Ludhiana"},
            {"district": "Amritsar", "market": "Amritsar"},
            {"district": "Patiala", "market": "Patiala"},
            {"district": "Jalandhar", "market": "Jalandhar"},
            {"district": "Bathinda", "market": "Bathinda"}
        ],
        "Haryana": [
            {"district": "Karnal", "market": "Karnal"},
            {"district": "Ambala", "market": "Ambala"},
            {"district": "Hisar", "market": "Hisar"},
            {"district": "Gurugram", "market": "Gurugram"},
            {"district": "Kurukshetra", "market": "Kurukshetra"}
        ],
        "Uttar Pradesh": [
            {"district": "Lucknow", "market": "Lucknow"},
            {"district": "Kanpur", "market": "Kanpur"},
            {"district": "Varanasi", "market": "Varanasi"},
            {"district": "Agra", "market": "Agra"},
            {"district": "Meerut", "market": "Meerut"}
        ],
        "Himachal Pradesh": [
            {"district": "Shimla", "market": "Shimla"},
            {"district": "Solan", "market": "Solan"},
            {"district": "Kangra", "market": "Dharamshala"},
            {"district": "Kullu", "market": "Kullu"},
            {"district": "Mandi", "market": "Mandi"}
        ]
    }
    
    # Return markets for the specified state or a default list
    return state_markets.get(state, [{"district": "Ludhiana", "market": "Ludhiana"}])
