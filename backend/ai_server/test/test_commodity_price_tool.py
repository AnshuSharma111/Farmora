"""
Test script for the consolidated commodity price tool.

This script tests the main functions in the commodity_price_tool.py module
to ensure they correctly fetch market prices based on user location.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import local modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from tools.commodity_price_tool import get_commodity_price, get_all_commodity_prices

def test_single_commodity():
    """Test getting price data for a single commodity"""
    print("==== Testing Single Commodity Lookup ====")
    
    # Test coordinates (near Chandigarh)
    lat = 30.7463
    lon = 76.6469
    commodity = "Rice"
    
    print(f"Getting price data for {commodity} at coordinates {lat}, {lon}")
    result = get_commodity_price(lat, lon, commodity, debug=True)
    
    print("\nResults:")
    if "error" not in result:
        print(f"State: {result['state']}")
        print(f"District: {result['district']}")
        print(f"Market: {result['market']}")
        print(f"Records found: {result['data_points']}")
        print(f"Latest price: ₹{result['latest_prices'].get('modal_price', 'N/A')}")
        print(f"Range: ₹{result['latest_prices'].get('min_price', 'N/A')} - ₹{result['latest_prices'].get('max_price', 'N/A')}")
        print(f"Date: {result['latest_prices'].get('date', 'N/A')}")
        print(f"Variety: {result['latest_prices'].get('variety', 'N/A')}")
    else:
        print(f"Error: {result['error']}")

def test_multiple_commodities():
    """Test getting price data for multiple commodities"""
    print("\n==== Testing Multiple Commodities Lookup ====")
    
    # Test coordinates (near Chandigarh)
    lat = 30.7463
    lon = 76.6469
    commodities = ["Rice", "Wheat", "Maize"]
    
    print(f"Getting price data for {', '.join(commodities)} at coordinates {lat}, {lon}")
    results = get_all_commodity_prices(lat, lon, commodities, debug=True)
    
    print("\nResults Summary:")
    for commodity, data in results.items():
        print(f"\n{commodity}:")
        if "error" not in data:
            print(f"  Market: {data['market']}, {data['district']}, {data['state']}")
            print(f"  Records: {data['data_points']}")
            if data['latest_prices']:
                print(f"  Price: ₹{data['latest_prices'].get('modal_price', 'N/A')} (₹{data['latest_prices'].get('min_price', 'N/A')} - ₹{data['latest_prices'].get('max_price', 'N/A')})")
                print(f"  Date: {data['latest_prices'].get('date', 'N/A')}")
                print(f"  Variety: {data['latest_prices'].get('variety', 'N/A')}")
            else:
                print("  No price data available")
        else:
            print(f"  Error: {data['error']}")

def test_integration_with_processing_pipeline():
    """Test integration with the processing pipeline"""
    print("\n==== Testing Integration with Processing Pipeline ====")
    
    # Import the processing module
    sys.path.append(str(Path(__file__).resolve().parent))
    try:
        from processing import process_query
        
        # Test parameters for a simulated query
        audio_path = "test_query.wav"  # This doesn't need to exist for this test
        language_code = "en"
        crops = ["Rice", "Wheat"]
        location = [30.7463, 76.6469]
        
        print(f"Simulating process_query with crops={crops}, location={location}")
        print("Note: This is a partial test that doesn't execute the full pipeline")
        print("Success if imports and parameters match expectations")
        print("\nMake sure your processing.py file now imports from commodity_price_tool.py:")
        print("from tools.commodity_price_tool import get_all_commodity_prices, get_commodity_price")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Ensure processing.py is correctly updated")

if __name__ == "__main__":
    # Run tests
    test_single_commodity()
    test_multiple_commodities()
    test_integration_with_processing_pipeline()
    
    print("\nAll tests completed!")
