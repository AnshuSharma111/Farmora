"""
Function to get prices for multiple commodities based on user location.
"""
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to import local modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from tools.commodity_price_tool import get_commodity_price

def get_commodity_prices(lat: float, lon: float, commodities: List[str], debug: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Gets price data for multiple commodities based on user location.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodities: List of commodity names to look up (e.g., ["Rice", "Wheat"])
        debug: Whether to print debug info and save debug screenshots
        
    Returns:
        Dictionary mapping commodity names to their price data results
    """
    results = {}
    
    for commodity in commodities:
        try:
            result = get_commodity_price(lat, lon, commodity, debug=debug)
            results[commodity] = result
        except Exception as e:
            # Handle exceptions for individual commodities but continue with others
            results[commodity] = {
                "error": f"Error retrieving data for {commodity}: {str(e)}",
                # Add seasonal info if available
                "seasonal_info": {
                    "growing_season": "Data not available",
                    "harvesting_period": "Data not available"
                }
            }
    
    return results

if __name__ == "__main__":
    # Example usage
    lat, lon = 28.7041, 77.1025  # Delhi
    commodities = ["Rice", "Wheat", "Tomato"]
    
    results = get_commodity_prices(lat, lon, commodities, debug=True)
    
    for commodity, data in results.items():
        print(f"\n=== {commodity} ===")
        if "error" not in data:
            print(f"Found price data in {data['market']}")
            if data['latest_prices']:
                price = data['latest_prices']['modal_price']
                date = data['latest_prices']['date']
                variety = data['latest_prices']['variety']
                print(f"Latest price: ₹{price} for {variety} on {date}")
            else:
                print("No price data available")
        else:
            print(f"Error: {data['error']}")
            if 'seasonal_info' in data:
                print("Seasonal information available")
