"""
Test script for the enhanced location-based commodity price lookup
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import the tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tools.geo_utils import (
    get_nearest_location_from_database,
    find_markets_by_coordinates,
    calculate_distance
)
from tools.scrape_commodity import scrape_commodity_by_location

def test_location_based_lookup():
    """
    Test the enhanced location-based commodity price lookup functionality.
    """
    print("Testing Enhanced Location-Based Commodity Price Lookup")
    print("-----------------------------------------------------")
    
    # Test coordinates (Punjab, near Mohali)
    lat, lon = 30.7463, 76.6469
    print(f"Using test coordinates: {lat}, {lon}")
    
    # Step 1: Get the nearest location from our database
    print("\n1. Finding nearest location in the database...")
    nearest_location = get_nearest_location_from_database(lat, lon)
    
    if nearest_location:
        print(f"Found nearest location: {nearest_location['district']}, {nearest_location['state']}")
        print(f"Nearest market: {nearest_location['market']} ({nearest_location['distance_km']:.2f} km away)")
    else:
        print("No location found in the database.")
    
    # Step 2: Find markets near the coordinates
    print("\n2. Finding markets near the coordinates...")
    markets = find_markets_by_coordinates(lat, lon)
    
    if markets:
        print(f"Found {len(markets)} nearby markets:")
        for i, market in enumerate(markets[:5]):  # Show first 5 markets
            print(f"  {i+1}. {market}")
        if len(markets) > 5:
            print(f"  ... and {len(markets)-5} more")
    else:
        print("No markets found near the coordinates.")
    
    # Step 3: Get price data for a commodity
    print("\n3. Getting price data for Rice...")
    commodity = "Rice"
    
    try:
        results = scrape_commodity_by_location(lat, lon, commodity)
        
        if "error" in results and results["error"]:
            print(f"Error: {results['error']}")
        else:
            print(f"Successfully retrieved data from {results.get('market')}")
            print(f"Location: {results.get('district')}, {results.get('state')}")
            
            latest = results.get('latest_prices', {})
            if latest:
                print(f"Latest price: ₹{latest.get('modal_price', 'N/A')} "
                      f"(₹{latest.get('min_price', 'N/A')} - ₹{latest.get('max_price', 'N/A')})")
                print(f"Variety: {latest.get('variety', 'Unknown')}")
                print(f"Date: {latest.get('date', 'Unknown')}")
                
            records = results.get('data', [])
            print(f"Total records: {len(records)}")
    except Exception as e:
        print(f"Error running test: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_location_based_lookup()
