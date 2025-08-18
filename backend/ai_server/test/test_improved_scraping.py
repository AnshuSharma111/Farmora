"""
Test script for the improved commodity price tool with fixed scraping functionality.

This script tests the updated table processing logic and fallback mechanisms to ensure 
it correctly handles the table structure and can retrieve market price data.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import local modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from tools.commodity_price_tool import get_commodity_price, get_all_commodity_prices

def test_with_known_data():
    """Test with a known commodity and location that should have data"""
    print("==== Testing with Known Data (Himachal Pradesh / Apple) ====")
    
    # Coordinates for Himachal Pradesh, where apple data is likely
    lat = 31.1048
    lon = 77.1734
    commodity = "Apple"
    
    print(f"Getting price data for {commodity} in Himachal Pradesh (coordinates: {lat}, {lon})")
    result = get_commodity_price(lat, lon, commodity, debug=True)
    
    print("\nResults:")
    if "error" not in result:
        print(f"State: {result['state']}")
        print(f"District: {result['district']}")
        print(f"Market: {result['market']}")
        print(f"Records found: {result['data_points']}")
        if result['latest_prices']:
            print(f"Latest price: ₹{result['latest_prices'].get('modal_price', 'N/A')}")
            print(f"Range: ₹{result['latest_prices'].get('min_price', 'N/A')} - ₹{result['latest_prices'].get('max_price', 'N/A')}")
            print(f"Date: {result['latest_prices'].get('date', 'N/A')}")
            print(f"Variety: {result['latest_prices'].get('variety', 'N/A')}")
        else:
            print("No price data available")
    else:
        print(f"Error: {result['error']}")

def test_multi_commodity():
    """Test with multiple commodities including a likely seasonal one"""
    print("\n==== Testing Multi-Commodity and Seasonal Fallbacks ====")
    
    # Coordinates near Delhi
    lat = 28.7041
    lon = 77.1025
    commodities = ["Rice", "Wheat", "Strawberry"]
    
    print(f"Getting price data for {commodities} near Delhi (coordinates: {lat}, {lon})")
    results = get_all_commodity_prices(lat, lon, commodities, debug=True)
    
    for commodity, result in results.items():
        print(f"\nResults for {commodity}:")
        if "error" not in result:
            print(f"State: {result['state']}")
            print(f"District: {result['district']}")
            print(f"Market: {result['market']}")
            print(f"Records found: {result['data_points']}")
            if result['latest_prices']:
                print(f"Latest price: ₹{result['latest_prices'].get('modal_price', 'N/A')}")
                print(f"Variety: {result['latest_prices'].get('variety', 'N/A')}")
                print(f"Date: {result['latest_prices'].get('date', 'N/A')}")
            else:
                print("No price data available")
                
            # Check for seasonal info fallback
            if 'seasonal_info' in result:
                print("Seasonal Information Available:")
                print(f"Growing Season: {result['seasonal_info'].get('growing_season', 'N/A')}")
                print(f"Harvesting Period: {result['seasonal_info'].get('harvesting_period', 'N/A')}")
        else:
            print(f"Error: {result['error']}")
            if 'seasonal_info' in result:
                print("Seasonal Information Available:")
                print(f"Growing Season: {result['seasonal_info'].get('growing_season', 'N/A')}")
                print(f"Harvesting Period: {result['seasonal_info'].get('harvesting_period', 'N/A')}")

def test_district_name_variants():
    """Test handling of district name variants (Hisar/Hissar, Gurugram/Gurgaon)"""
    print("\n==== Testing District Name Variants ====")
    
    # Coordinates for Gurugram
    lat = 28.4595
    lon = 77.0266
    commodity = "Rice"
    
    print(f"Getting price data for {commodity} in Gurugram (coordinates: {lat}, {lon})")
    result = get_commodity_price(lat, lon, commodity, debug=True)
    
    print("\nResults:")
    if "error" not in result:
        print(f"State: {result['state']}")
        print(f"District: {result['district']}") # Should show normalization working
        print(f"Market: {result['market']}")
        if result['latest_prices']:
            print(f"Latest price: ₹{result['latest_prices'].get('modal_price', 'N/A')}")
        else:
            print("No price data available")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    test_with_known_data()
    test_multi_commodity()
    test_district_name_variants()
    
    print("\nAll tests completed!")
