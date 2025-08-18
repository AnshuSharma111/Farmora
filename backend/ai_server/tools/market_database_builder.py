"""
Market Data Scraper for Agmarknet

This script creates a comprehensive dataset of all states, districts, markets, and commodities
available in the Agmarknet portal. The data is stored locally to provide reliable offline
access and enable geographic proximity calculations.
"""

import time
import json
import os
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Try to import geopy for distance calculation, but provide fallback if not available
try:
    from geopy.distance import geodesic
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False
    
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Constants
AGMARKNET_URL = "https://agmarknet.gov.in/PriceAndArrivals/DatewiseCommodityReport.aspx"
DATA_DIR = Path(__file__).parent.parent / "data"
MARKETS_FILE = DATA_DIR / "markets_database.json"
GEOCODED_MARKETS_FILE = DATA_DIR / "geocoded_markets.json"

# Ensure the data directory exists
DATA_DIR.mkdir(exist_ok=True)

def calculate_distance(coord1, coord2):
    """
    Calculate the distance between two coordinates in kilometers.
    Uses geopy if available, otherwise falls back to haversine formula.
    """
    if HAS_GEOPY:
        return geodesic(coord1, coord2).kilometers
    else:
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

def setup_driver():
    """Set up and return a Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_dropdown_options(driver, dropdown_id):
    """Get all options from a dropdown element."""
    try:
        dropdown = Select(driver.find_element("id", dropdown_id))
        options = [(option.get_attribute("value"), option.text) for option in dropdown.options]
        # Filter out the first option which is usually a placeholder like "-- Select --"
        if options and (options[0][0] == "" or options[0][0] == "0"):
            options = options[1:]
        return options
    except Exception:
        # Silent failure - logging could be added here instead
        return []

def select_dropdown_option(driver, dropdown_id, option_value):
    """Select an option in a dropdown by its value."""
    try:
        dropdown = Select(driver.find_element("id", dropdown_id))
        dropdown.select_by_value(option_value)
        time.sleep(1)  # Give time for any dependent dropdowns to update
        return True
    except Exception:
        # Silent failure - logging could be added here instead
        return False

def get_all_states(driver):
    """Get all states from the state dropdown."""
    return get_dropdown_options(driver, 'ddlState')

def get_districts_for_state(driver, state_value):
    """Get all districts for a given state."""
    # Select the state first
    if not select_dropdown_option(driver, 'ddlState', state_value):
        return []
    
    # Then get all districts
    return get_dropdown_options(driver, 'ddlDistrict')

def get_markets_for_district(driver, state_value, district_value):
    """Get all markets for a given district in a state."""
    # Select the state first
    if not select_dropdown_option(driver, 'ddlState', state_value):
        return []
    
    # Then select the district
    if not select_dropdown_option(driver, 'ddlDistrict', district_value):
        return []
    
    # Finally get all markets
    return get_dropdown_options(driver, 'ddlMarket')

def get_all_commodities(driver):
    """Get all commodities from the commodity dropdown."""
    return get_dropdown_options(driver, 'ddlCommodity')

def scrape_all_market_data():
    """
    Scrape all states, districts, markets, and commodities from Agmarknet.
    """
    driver = setup_driver()
    
    try:
        driver.get(AGMARKNET_URL)
        time.sleep(3)  # Wait for page to load
        
        # Get all states
        states = get_all_states(driver)
        
        market_data = {"states": {}, "commodities": []}
        
        # Get all commodities first
        commodities = get_all_commodities(driver)
        market_data["commodities"] = commodities
        
        # Process each state
        for state_value, state_name in states:
            market_data["states"][state_name] = {"districts": {}, "value": state_value}
            
            # Get all districts for this state
            districts = get_districts_for_state(driver, state_value)
            
            # Process each district
            for district_value, district_name in districts:
                market_data["states"][state_name]["districts"][district_name] = {
                    "value": district_value,
                    "markets": {}
                }
                
                # Get all markets for this district
                markets = get_markets_for_district(driver, state_value, district_value)
                
                # Store market information
                for market_value, market_name in markets:
                    market_data["states"][state_name]["districts"][district_name]["markets"][market_name] = {
                        "value": market_value
                    }
        
        # Save the data
        with open(MARKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(market_data, f, ensure_ascii=False, indent=2)
            
        return market_data
        
    except Exception:
        return None
    finally:
        driver.quit()

def load_market_data():
    """Load market data from file if it exists, otherwise scrape it."""
    if os.path.exists(MARKETS_FILE):
        with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return scrape_all_market_data()

def geocode_markets(market_data):
    """
    Add approximate geographic coordinates to each market.
    
    For a production system, you would use a geocoding service like Google Maps or Nominatim.
    Here, we'll use approximate coordinates based on the district center.
    """
    # Create dummy geocoded data (this would normally come from a geocoding service)
    # Format: {"State": {"District": {"Market": [lat, lon]}}
    
    # Define coordinates for state centers (approximate)
    state_coords = {
        "Punjab": [30.9010, 75.8573],          # Ludhiana
        "Haryana": [29.0588, 76.0856],          # Rohtak
        "Himachal Pradesh": [31.1048, 77.1734], # Shimla
        "Uttar Pradesh": [26.8467, 80.9462],    # Lucknow
        "Maharashtra": [19.0760, 72.8777],      # Mumbai
        "Karnataka": [12.9716, 77.5946],        # Bangalore
        "Tamil Nadu": [13.0827, 80.2707],       # Chennai
        "Gujarat": [23.0225, 72.5714],          # Ahmedabad
        "Rajasthan": [26.9124, 75.7873],        # Jaipur
        "Bihar": [25.5941, 85.1376],            # Patna
        # Add more states as needed
    }
    
    # Small offsets to distribute markets around district centers
    offsets = [
        [0.05, 0.05], [-0.05, 0.05], [0.05, -0.05], [-0.05, -0.05],
        [0.1, 0], [-0.1, 0], [0, 0.1], [0, -0.1],
        [0.15, 0.15], [-0.15, 0.15], [0.15, -0.15], [-0.15, -0.15]
    ]
    
    geocoded_markets = {}
    
    for state_name, state_data in market_data["states"].items():
        geocoded_markets[state_name] = {}
        state_lat, state_lon = state_coords.get(state_name, [20.5937, 78.9629])  # Default to center of India
        
        for district_name, district_data in state_data["districts"].items():
            geocoded_markets[state_name][district_name] = {}
            
            # Use a simple algorithm to distribute district centers around the state
            # This is just for demonstration - in production, use actual geocoding
            district_hash = sum(ord(c) for c in district_name)
            district_idx = district_hash % len(offsets)
            district_offset = offsets[district_idx]
            
            district_lat = state_lat + district_offset[0]
            district_lon = state_lon + district_offset[1]
            
            market_idx = 0
            for market_name in district_data["markets"].keys():
                # Distribute markets around the district center
                market_offset = offsets[market_idx % len(offsets)]
                market_lat = district_lat + market_offset[0] * 0.5
                market_lon = district_lon + market_offset[1] * 0.5
                
                geocoded_markets[state_name][district_name][market_name] = [market_lat, market_lon]
                market_idx += 1
    
    # Save the geocoded data
    with open(GEOCODED_MARKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(geocoded_markets, f, ensure_ascii=False, indent=2)
        
    return geocoded_markets

def find_nearest_market(lat, lon, state=None, district=None):
    """
    Find the nearest market to the given coordinates.
    Optionally filter by state and district.
    """
    # Load geocoded market data
    if os.path.exists(GEOCODED_MARKETS_FILE):
        with open(GEOCODED_MARKETS_FILE, 'r', encoding='utf-8') as f:
            geocoded_markets = json.load(f)
    else:
        market_data = load_market_data()
        geocoded_markets = geocode_markets(market_data)
    
    nearest_market = None
    nearest_distance = float('inf')
    nearest_state = None
    nearest_district = None
    
    for state_name, districts in geocoded_markets.items():
        # Skip if a specific state is requested and this isn't it
        if state and state != state_name:
            continue
            
        for district_name, markets in districts.items():
            # Skip if a specific district is requested and this isn't it
            if district and district != district_name:
                continue
                
            for market_name, coords in markets.items():
                market_lat, market_lon = coords
                distance = calculate_distance((lat, lon), (market_lat, market_lon))
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_market = market_name
                    nearest_state = state_name
                    nearest_district = district_name
    
    return {
        "market": nearest_market,
        "district": nearest_district,
        "state": nearest_state,
        "distance_km": nearest_distance,
        "coordinates": geocoded_markets.get(nearest_state, {}).get(nearest_district, {}).get(nearest_market)
    }

if __name__ == "__main__":
    # If the files don't exist, scrape and create them
    if not os.path.exists(MARKETS_FILE):
        market_data = scrape_all_market_data()
        if market_data and not os.path.exists(GEOCODED_MARKETS_FILE):
            geocode_markets(market_data)
    
    # Uncomment to force data refresh
    # market_data = scrape_all_market_data()
    # if market_data:
    #     geocode_markets(market_data)
            
    # Test the nearest market finder with some example coordinates
    test_coordinates = [
        (30.7463, 76.6469, "Punjab, Mohali area"),
        (30.9010, 75.8573, "Punjab, Ludhiana area"),
        (28.4595, 77.0266, "Haryana, Gurugram area")
    ]
    
    for lat, lon, description in test_coordinates:
        nearest = find_nearest_market(lat, lon)
        # Results can be used for further processing or displayed as needed
