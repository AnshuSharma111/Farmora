"""
Enhanced Geolocation utilities for Farmora AI Server.

This module provides functions to determine administrative regions from
geographical coordinates, and to find the nearest market to a given location.
"""

import requests
import math
import json
from typing import Tuple, Optional, Dict, List, Any
from pathlib import Path

# We'll use OpenStreetMap's Nominatim API for reverse geocoding
# It's free and doesn't require an API key, but has usage limits
NOMINATIM_API = "https://nominatim.openstreetmap.org/reverse"

# Define paths to data files
DATA_DIR = Path(__file__).parent.parent / "data"
MARKETS_FILE = DATA_DIR / "geocoded_markets.json"

def load_market_data() -> Dict[str, Dict[str, Dict[str, List[float]]]]:
    """
    Load market data from the geocoded_markets.json file.
    
    Returns:
        Nested dictionary with market data organized by state, district, and market name
    """
    try:
        with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Market data file not found at {MARKETS_FILE}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in market data file {MARKETS_FILE}")
        return {}

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the distance between two coordinates in kilometers.
    Uses the haversine formula for accurate earth distance calculations.
    
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

def get_state_district(lat: float, lon: float) -> Tuple[str, Optional[str]]:
    """
    Get the state and district name for given latitude and longitude.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Tuple of (state_name, district_name) where district_name may be None if not found
    """

    # Hit the location API
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "zoom": 10,
        "accept-language": "en"
    }

    headers = {
        "User-Agent": "Farmora/1.0 (farmora.app; contact@farmora.app)"
    }

    try:
        response = requests.get(NOMINATIM_API, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "address" not in data:
            raise RuntimeError("No address information found in the API response")
            
        address = data.get("address", {})

        if not address:
            return {}

        result = {"State" : address.get('state'), "County": address.get('county'), "District": address.get('state_district')}
        
        return result
    except Exception as e:
        raise e

def get_nearest_market(lat: float, lon: float, debug: bool = False) -> Dict[str, Any]:
    """
    Find the nearest market to the given coordinates.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        debug: Print debug information during search
        
    Returns:
        Dictionary with details of the nearest market or empty dict if none found
    """
    try:
        # Get location info
        state_district_data = get_state_district(lat, lon)
        state = state_district_data.get("State")
        district = state_district_data.get("District")
        county = state_district_data.get("County")
        
        if debug:
            print(f"Location info: State={state}, District={district}, County={county}")
        
        # Load market data
        markets_data = load_market_data()
        if not markets_data:
            print("No market data found")
            return {}
        
        # Create a list to store all potential markets with their distances
        all_markets = []
        
        # If we have state info, try to search within that state first
        if state and state in markets_data:
            search_states = [state]
            if debug:
                print(f"Searching in state: {state}")
        else:
            # Otherwise search all states
            search_states = markets_data.keys()
            if debug:
                print(f"State not found in market data. Searching in all {len(search_states)} states")
        
        # Search through all relevant states
        for state_name in search_states:
            state_markets = markets_data.get(state_name, {})
            
            # If we have district info and it exists in the state data, search there first
            if district and district in state_markets:
                search_districts = [district]
                if debug:
                    print(f"  Searching in district: {district} within {state_name}")
            elif county and county in state_markets:
                search_districts = [county]
                if debug:
                    print(f"  Searching in county: {county} within {state_name}")
            else:
                # Otherwise search all districts in this state
                search_districts = state_markets.keys()
                if debug:
                    print(f"  District/County not found in {state_name}. Searching in all {len(search_districts)} districts")
            
            # Search through relevant districts
            for district_name in search_districts:
                district_markets = state_markets.get(district_name, {})
                
                if debug:
                    print(f"    Checking {len(district_markets)} markets in {district_name}")
                
                # Search through each market in this district
                for market_name, coords in district_markets.items():
                    # Skip markets with invalid or empty coordinates
                    if not coords or len(coords) < 2:
                        continue
                    
                    # Some entries might have only one coordinate or might be empty arrays
                    try:
                        # Make sure coordinates are valid numbers
                        if coords[0] is None or coords[1] is None:
                            continue
                            
                        market_lat = float(coords[0])
                        market_lon = float(coords[1])
                        
                        # Check if the coordinates make sense (basic validation)
                        if not (-90 <= market_lat <= 90) or not (-180 <= market_lon <= 180):
                            continue
                        
                        # Calculate distance
                        market_coords = (market_lat, market_lon)
                        user_coords = (lat, lon)
                        distance = calculate_distance(user_coords, market_coords)
                        
                        # Store market info
                        all_markets.append({
                            "market_name": market_name,
                            "state": state_name,
                            "district": district_name,
                            "latitude": market_lat,
                            "longitude": market_lon,
                            "distance_km": distance
                        })
                        
                    except (IndexError, TypeError, ValueError):
                        continue
        
        # Sort all markets by distance to get the truly nearest one
        all_markets.sort(key=lambda x: x["distance_km"])
        
        # Return results using the first market from the sorted list
        if all_markets:
            nearest = all_markets[0]
            return {
                "market_name": nearest["market_name"],
                "state": nearest["state"],
                "district": nearest["district"],
                "latitude": nearest["latitude"],
                "longitude": nearest["longitude"],
                "distance_km": round(nearest["distance_km"], 2)
            }
        else:
            return {}
            
    except Exception as e:
        print(f"Error finding nearest market: {e}")
        return {}

def main():
    # test
    print("Getting location info for various coordinates: ")
    coords = [
        [30.764782, 76.573887, "Chandigarh Region"],
    ]

    for i, (lat, lon, desc) in enumerate(coords):
        print(f"\nCoordinate {i} ({desc}):")
        print(f"Latitude: {lat}, Longitude: {lon}")
        
        # Get and print the location info
        loc_info = get_state_district(lat, lon)
        print(f"Location data from API: {loc_info}")
        
        # Get nearest market
        res = get_nearest_market(lat, lon, debug=True)
        
        if res:
            print(f"\nNearest market found: {res['market_name']}")
            print(f"State: {res['state']}")
            print(f"District: {res['district']}")
            print(f"Coordinates: ({res['latitude']}, {res['longitude']})")
            print(f"Distance: {res['distance_km']} km")
        else:
            print("\nNo market found!")

if __name__ == "__main__":
    main()