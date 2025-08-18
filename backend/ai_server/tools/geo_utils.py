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
    # Predefined location cache for common coordinates to handle network issues
    location_cache = {
        # Punjab locations
        (30.7463, 76.6469): {"address": {"state": "Punjab", "county": "Kharar"}},
        (30.9010, 75.8573): {"address": {"state": "Punjab", "county": "Ludhiana"}},
        (31.6340, 74.8723): {"address": {"state": "Punjab", "county": "Amritsar"}},
        (30.3398, 76.3869): {"address": {"state": "Punjab", "county": "Patiala"}},
        (31.3260, 75.5762): {"address": {"state": "Punjab", "county": "Jalandhar"}},
    
        # Haryana locations
        (28.4595, 77.0266): {"address": {"state": "Haryana", "county": "Gurugram"}},
        (29.7051, 76.9734): {"address": {"state": "Haryana", "county": "Karnal"}},
        (28.4089, 77.3178): {"address": {"state": "Haryana", "county": "Faridabad"}},
        
        # Himachal Pradesh locations
        (31.1048, 77.1734): {"address": {"state": "Himachal Pradesh", "county": "Shimla"}},
        (32.2396, 76.3219): {"address": {"state": "Himachal Pradesh", "county": "Kangra"}},
        
        # Default for unknown locations
        (0, 0): {"address": {"state": "Delhi", "county": "New Delhi"}}
    }
    
    # Check if we have cached data for these exact coordinates
    if (lat, lon) in location_cache:
        return location_cache[(lat, lon)]
    
    # Find the closest match for approximate coordinates
    closest_coords = None
    min_distance = float('inf')
    
    for coords in location_cache:
        # Skip the default coordinates
        if coords == (0, 0):
            continue
            
        # Calculate distance between input coordinates and cached coordinates
        dist = calculate_distance((lat, lon), coords)
        
        # If within a reasonable threshold (approximately 10-15km)
        if dist < 15 and dist < min_distance:
            min_distance = dist
            closest_coords = coords
    
    # If we found a close match, use it
    if closest_coords:
        return location_cache[closest_coords]
    
    # If no cached data found, try the API
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
        
    except Exception:
        # Determine rough region based on coordinates
        if 27 <= lat <= 32 and 73 <= lon <= 78:
            if lat > 30.5:
                return location_cache[(30.9010, 75.8573)]  # Punjab (Ludhiana)
            elif lon > 76:
                return location_cache[(31.1048, 77.1734)]  # Himachal Pradesh (Shimla)
            else:
                return location_cache[(28.4595, 77.0266)]  # Haryana (Gurugram)
        else:
            # Default fallback
            return location_cache[(0, 0)]

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
    
    # Convert to lowercase for case-insensitive matching
    district_lower = cleaned_district.lower().strip()
    
    # Define common district name mappings, expanded from the previous version
    district_mappings = {
        # Punjab
        "kharar": "Mohali",      # Kharar is in Mohali district
        "mohali": "Mohali",
        "sas nagar": "Mohali",   # SAS Nagar is the official name of Mohali
        "sahibzada ajit singh nagar": "Mohali",
        "s.a.s. nagar": "Mohali",
        "kapurthala": "Kapurthala",
        "jalandhar": "Jalandhar",
        "ludhiana": "Ludhiana",
        "patiala": "Patiala",
        "amritsar": "Amritsar",
        "firozpur": "Ferozepur",  # Handle alternate spellings
        "ferozepur": "Ferozepur",
        "faridkot": "Faridkot",
        "hoshiarpur": "Hoshiarpur",
        "mansa": "Mansa",
        "moga": "Moga",
        "muktsar": "Sri Muktsar Sahib",
        "sri muktsar sahib": "Sri Muktsar Sahib",
        "nawanshahr": "Shahid Bhagat Singh Nagar",
        "shahid bhagat singh nagar": "Shahid Bhagat Singh Nagar",
        "sbs nagar": "Shahid Bhagat Singh Nagar",
        
        # Haryana
        "gurugram": "Gurugram",
        "gurgaon": "Gurugram",  # Old name
        "karnal": "Karnal",
        "ambala": "Ambala",
        "hisar": "Hisar",
        "faridabad": "Faridabad",
        "panipat": "Panipat",
        "bhiwani": "Bhiwani",
        "jhajjar": "Jhajjar",
        "jind": "Jind",
        "kaithal": "Kaithal",
        "kurukshetra": "Kurukshetra",
        "mahendragarh": "Mahendragarh",
        "palwal": "Palwal",
        "rewari": "Rewari",
        "rohtak": "Rohtak",
        "sirsa": "Sirsa",
        "sonipat": "Sonipat",
        
        # Himachal Pradesh
        "shimla": "Shimla",
        "solan": "Solan",
        "kangra": "Kangra",
        "una": "Una",
        "hamirpur": "Hamirpur",
        "bilaspur": "Bilaspur",
        "mandi": "Mandi",
        "kullu": "Kullu",
        "lahaul and spiti": "Lahaul and Spiti",
        "lahaul spiti": "Lahaul and Spiti",
        "kinnaur": "Kinnaur",
        "chamba": "Chamba",
        "sirmaur": "Sirmaur",
    }
    
    # Return the normalized name if found, otherwise return the cleaned district
    return district_mappings.get(district_lower, cleaned_district)

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
    
    # Fallback to hardcoded values
    # Dictionary of states -> districts -> markets
    markets_by_district = {
        "Punjab": {
            "Ludhiana": ["Ludhiana", "Khanna", "Jagraon"],
            "Amritsar": ["Amritsar", "Jandiala", "Rayya"],
            "Patiala": ["Patiala", "Rajpura", "Nabha"],
            "Mohali": ["Sri Har Gobindpur", "Kharar", "Mohali"],
            "Kapurthala": ["Kapurthala", "Sultanpur Lodhi", "Phagwara"],
            "Jalandhar": ["Jalandhar", "Phillaur", "Nakodar"],
            "Bathinda": ["Bathinda", "Rampura Phul", "Talwandi Sabo"],
            "Gurdaspur": ["Gurdaspur", "Batala", "Dera Baba Nanak"],
            "Hoshiarpur": ["Hoshiarpur", "Garhshankar", "Dasuya"],
            "Fatehgarh": ["Fatehgarh", "Amloh", "Bassi Pathana"]
        },
        "Haryana": {
            "Karnal": ["Karnal", "Assandh", "Taraori"],
            "Ambala": ["Ambala", "Naraingarh", "Barara"],
            "Hisar": ["Hisar", "Hansi", "Barwala"],
            "Gurugram": ["Gurugram", "Sohna", "Pataudi"],
            "Faridabad": ["Faridabad", "Ballabgarh", "Palwal"],
            "Panipat": ["Panipat", "Samalkha", "Israna"]
        },
        "Himachal Pradesh": {
            "Shimla": ["Shimla", "Theog", "Rohru"],
            "Solan": ["Solan", "Arki", "Kasauli"],
            "Mandi": ["Mandi", "Sundernagar", "Jogindernagar"],
            "Kangra": ["Dharamshala", "Palampur", "Kangra"],
            "Kullu": ["Kullu", "Manali", "Bhuntar"]
        },
        "Uttar Pradesh": {
            "Lucknow": ["Lucknow", "Bakshi ka Talab", "Mohanlalganj"],
            "Kanpur": ["Kanpur", "Bilhaur", "Ghatampur"],
            "Agra": ["Agra", "Fatehpur Sikri", "Etmadpur"]
        }
    }
    
    # If we have markets for this state and normalized district
    if state in markets_by_district and normalized_district in markets_by_district[state]:
        print(f"Found markets in {normalized_district}, {state}")
        return markets_by_district[state][normalized_district]
    
    # Try with original district name if normalized didn't match
    if state in markets_by_district and district in markets_by_district[state]:
        print(f"Found markets in {district}, {state}")
        return markets_by_district[state][district]
    
    # If we have the state but not the district
    if state in markets_by_district:
        # Return markets from the first district we have
        first_district = next(iter(markets_by_district[state]))
        print(f"Warning: District '{district}' not found in {state}. Using '{first_district}' instead.")
        return markets_by_district[state][first_district]
        
    # Fallback to default markets
    print(f"Warning: No markets found for {state}. Using default markets.")
    return ["Nearest Market", "Central Market", "Regional Market"]


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

def get_common_crops(lat: float, lon: float) -> List[str]:
    """
    Returns a list of common crops grown in the region near the provided coordinates.
    This is a simplified implementation - a real implementation would use climate data,
    soil types, and actual agricultural data.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        List of common crop names in the region
    """
    # For demonstration, using a simplified approach based on rough geographical regions
    # In a real implementation, this would be much more sophisticated
    
    # North India
    if lat > 28.0:
        if lon < 77.0:  # Northwest (Punjab, Haryana)
            return ["Wheat", "Rice", "Cotton", "Maize"]
        else:  # Northeast (UP, Bihar)
            return ["Rice", "Wheat", "Sugarcane", "Potato"]
    # Central India
    elif lat > 20.0:
        if lon < 78.0:  # West Central (Maharashtra, Gujarat)
            return ["Cotton", "Groundnut", "Sorghum", "Millet"]
        else:  # East Central (Odisha, Jharkhand)
            return ["Rice", "Maize", "Pulses", "Oilseeds"]
    # South India
    else:
        if lon < 78.0:  # Southwest (Karnataka, Kerala)
            return ["Coffee", "Spices", "Rice", "Coconut"]
        else:  # Southeast (Tamil Nadu, Andhra Pradesh)
            return ["Rice", "Sugarcane", "Groundnut", "Cotton"]
