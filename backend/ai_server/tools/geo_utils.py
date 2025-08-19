"""
Enhanced Geolocation utilities for Farmora AI Server.

This module provides functions to determine administrative regions from
geographical coordinates, and to find the nearest market to a given location.
"""

import requests
import json
import os
import math
from typing import Dict, Tuple, Optional, List, Any
from pathlib import Path

# We'll use OpenStreetMap's Nominatim API for reverse geocoding
# It's free and doesn't require an API key, but has usage limits
NOMINATIM_API = "https://nominatim.openstreetmap.org/reverse"

# Define paths to data files
DATA_DIR = Path(__file__).parent.parent / "data"
MARKETS_FILE = DATA_DIR / "markets_database.json"
GEOCODED_MARKETS_FILE = DATA_DIR / "geocoded_markets.json"

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

def get_location_info(lat: float, lon: float) -> Dict:
    """
    Get location information for given latitude and longitude using reverse geocoding.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Dictionary with location details including state, district, and other admin levels
    """

    # Try the API
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
            
        return data

    except Exception as e:
        raise e

def get_state_district(lat: float, lon: float) -> Tuple[str, Optional[str]]:
    """
    Get the state and district name for given latitude and longitude.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        Tuple of (state_name, district_name) where district_name may be None if not found
    """
    # First try using the geocoded markets database for more accurate results
    nearest_location = get_nearest_location_from_database(lat, lon)
    if nearest_location:
        return nearest_location["state"], nearest_location["district"]

    # If that fails, fall back to the location API
    location_data = get_location_info(lat, lon)
    address = location_data.get("address", {})
    
    # In India, the state is typically in the "state" field
    state = address.get("state")
    
    # District can be in "county", "district", or "state_district" depending on the region
    district = (
        address.get("county") or 
        address.get("district") or 
        address.get("state_district")
    )
    
    # Clean up the district name using our normalize function
    if district:
        district = normalize_district_name(district)
    
    if not state:
        # Fallback to a default state if we couldn't determine it
        state = "Punjab"
    
    return state, district

def normalize_district_name(district: str) -> str:
    """
    Normalizes district names by handling common variations, alternate spellings, 
    and removing suffixes like Tahsil, District, etc.
    
    Args:
        district: District name to normalize
        
    Returns:
        Normalized district name
    """
    import re
    
    if not district:
        return ""
    
    # First, remove common suffixes like "Tahsil", "District", etc.
    suffixes = ["Tahsil", "District", "Tehsil", "Taluka", "Division", "Taluk", "Mandal", "Subdivision"]
    
    # Create a pattern to match any of these suffixes at the end of the string
    pattern = r"\s+(?:" + "|".join(suffixes) + r")\b"
    cleaned_district = re.sub(pattern, "", district, flags=re.IGNORECASE)

    # Return the normalized name if found, otherwise return the cleaned district
    return cleaned_district

def load_market_database() -> Dict:
    """
    Load the market database from file.
    
    Returns:
        Dictionary containing the market database or empty dict if not found
    """
    if os.path.exists(MARKETS_FILE):
        try:
            with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_geocoded_markets() -> Dict:
    """
    Load the geocoded markets database from file.
    
    Returns:
        Dictionary containing the geocoded markets or empty dict if not found
    """
    if os.path.exists(GEOCODED_MARKETS_FILE):
        try:
            with open(GEOCODED_MARKETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_nearest_location_from_database(lat: float, lon: float) -> Dict:
    """
    Find the nearest state, district, and market from the geocoded markets database.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        Dictionary with the nearest state, district, and market, or empty dict if not found
    """
    geocoded_markets = load_geocoded_markets()
    if not geocoded_markets:
        return {}
    
    nearest_market = None
    nearest_distance = float('inf')
    nearest_state = None
    nearest_district = None
    
    for state_name, districts in geocoded_markets.items():
        for district_name, markets in districts.items():
            for market_name, coords in markets.items():
                market_lat, market_lon = coords
                distance = calculate_distance((lat, lon), (market_lat, market_lon))
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_market = market_name
                    nearest_state = state_name
                    nearest_district = district_name
    
    if nearest_state:
        return {
            "market": nearest_market,
            "district": nearest_district,
            "state": nearest_state,
            "distance_km": nearest_distance
        }
    
    return {}

def get_nearest_markets(state: str, district: str, commodity: str = None) -> List[str]:
    """
    Returns a list of markets in the given district.
    First tries to use the market database, and falls back to hardcoded values if not available.
    
    Args:
        state: State name
        district: District name
        commodity: Optional commodity name (not used in current implementation)
        
    Returns:
        List of market names in the district
    """
    # Normalize the district name to handle variations
    normalized_district = normalize_district_name(district)
    
    # Try to use the market database first
    market_data = load_market_database()
    
    if market_data and "states" in market_data:
        # Find the state
        state_data = None
        for state_name, state_info in market_data["states"].items():
            if state_name.lower() == state.lower():
                state_data = state_info
                break
                
        if state_data and "districts" in state_data:
            # Find the district
            district_data = None
            for district_name, district_info in state_data["districts"].items():
                if district_name.lower() == normalized_district.lower():
                    district_data = district_info
                    break
            
            if district_data and "markets" in district_data:
                # Return all markets in this district
                return list(district_data["markets"].keys())
        
    # Fallback to default markets
    return []


def find_markets_by_coordinates(lat: float, lon: float, commodity: str = None) -> List[str]:
    """
    Find markets near the given coordinates that sell the specified commodity.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodity: Optional commodity name to filter by
        
    Returns:
        List of market names near the coordinates
    """
    # First find the nearest location (state and district)
    nearest_location = get_nearest_location_from_database(lat, lon)
    
    if nearest_location:
        # If we found a market in the database, get all markets in that district
        state = nearest_location["state"]
        district = nearest_location["district"]
        
        # Load the markets for this state and district
        market_data = load_market_database()
        
        if market_data and "states" in market_data:
            # Find the state
            if state in market_data["states"]:
                state_data = market_data["states"][state]
                
                # Find the district
                if "districts" in state_data and district in state_data["districts"]:
                    district_data = state_data["districts"][district]
                    
                    # Get all markets in this district
                    if "markets" in district_data:
                        markets = list(district_data["markets"].keys())
                        
                        # Return the found markets, with the nearest one first
                        if nearest_location["market"] in markets:
                            # Reorder to put the nearest market first
                            markets.remove(nearest_location["market"])
                            markets.insert(0, nearest_location["market"])
                        
                        return markets
    
    # If we couldn't find markets in the database, fall back to traditional method
    state, district = get_state_district(lat, lon)
    return get_nearest_markets(state, district, commodity)

def main():
    # test
    print("Getting location info for various coordinates: ")
    coords = [
        [30.74632, 76.64689],
        [31.583, 78.417]
    ]

if __name__ == "__main__":
    main()