"""
Updated location-based commodity price lookup script.

This script enhances the original commodity price lookup to:
1. Accurately find the nearest district to user coordinates using geographic distance
2. Try multiple markets in the district until data is found
3. Fallback to known major markets in the state if needed
"""

import sys
import os
from pathlib import Path
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path to import local modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from tools.scrape_commodity import scrape_commodity
from tools.enhanced_geo_utils import find_nearest_market_and_district, get_alternate_markets

def get_commodity_prices_by_location(
    lat: float, 
    lon: float, 
    commodity: str,
    debug: bool = True
) -> Dict[str, Any]:
    """
    Get commodity prices using enhanced location-based lookup.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodity: Commodity name to lookup (e.g., "Rice", "Wheat")
        debug: Whether to enable debug mode with verbose output
        
    Returns:
        Dictionary with price data and location information
    """
    if debug:
        print(f"Testing Enhanced Location-Based Commodity Price Lookup")
        print(f"-----------------------------------------------------")
        print(f"Using test coordinates: {lat}, {lon}\n")
    
    # Step 1: Find the nearest location (state, district, markets)
    if debug:
        print(f"1. Finding nearest location in the database...")
    
    location_info = find_nearest_market_and_district(lat, lon)
    
    state = location_info["state"]
    district = location_info["district"]
    markets = location_info["markets"]
    primary_market = location_info["primary_market"]
    distance = location_info["distance_km"]
    
    if debug:
        print(f"Found nearest location: {district}, {state}")
        print(f"Using nearest market to coordinates: {primary_market} ({distance:.2f} km away)\n")
        
    # Step 2: Try to scrape price data for the primary market
    if debug:
        print(f"2. Scraping price data for {commodity}...")
        print(f"Will attempt to retrieve prices for {commodity} from the market {primary_market} in {district}, {state}\n")
    
    # Set date range (2 weeks ago to today)
    today = datetime.datetime.now()
    two_weeks_ago = today - datetime.timedelta(days=14)
    # Using correct format - note we need to use lowercase %Y for current year format
    date_from = two_weeks_ago.strftime('%d-%b-%Y')
    date_to = today.strftime('%d-%b-%Y')
    
    # Try the primary market first
    market_data = None
    success_market = None
    
    try:
        market_data = scrape_commodity(
            state=state,
            district=district,
            market=primary_market,
            commodity=commodity,
            price_arrival="Both",
            date_from=date_from,
            date_to=date_to,
            debug=debug
        )
        success_market = primary_market
    except Exception as e:
        if debug:
            print(f"Error in scrape_commodity: {str(e)}")
        market_data = None
    
    # If no data found in primary market, try other markets in the district
    if not market_data or len(market_data) == 0:
        if debug:
            print(f"\nNo market data found for {commodity} in {primary_market}. Trying other markets in {district}...")
        
        for market in markets:
            if market == primary_market:
                continue  # Skip, we already tried this one
            
            try:
                if debug:
                    print(f"Trying another market: {market}")
                
                market_data = scrape_commodity(
                    state=state,
                    district=district,
                    market=market,
                    commodity=commodity,
                    price_arrival="Both",
                    date_from=date_from,
                    date_to=date_to,
                    debug=debug
                )
                
                if market_data and len(market_data) > 0:
                    success_market = market
                    break
            except Exception as e:
                if debug:
                    print(f"Error in scrape_commodity: {str(e)}")
                continue
    
    # If still no data, try major markets in the state
    if not market_data or len(market_data) == 0:
        if debug:
            print(f"\nTrying a different area. Using {state} state with major markets...")
        
        alternate_markets = get_alternate_markets(state, commodity)
        
        for market_info in alternate_markets:
            alt_district = market_info["district"]
            alt_market = market_info["market"]
            
            if alt_district == district and alt_market == primary_market:
                continue  # Skip, we already tried this one
            
            try:
                if debug:
                    print(f"Trying {alt_district} district with {alt_market} market...")
                
                market_data = scrape_commodity(
                    state=state,
                    district=alt_district,
                    market=alt_market,
                    commodity=commodity,
                    price_arrival="Both",
                    date_from=date_from,
                    date_to=date_to,
                    debug=debug
                )
                
                if market_data and len(market_data) > 0:
                    success_market = alt_market
                    district = alt_district
                    break
            except Exception as e:
                if debug:
                    print(f"Error in scrape_commodity: {str(e)}")
                continue
    
    # Process results
    result = {
        "state": state,
        "district": district,
        "market": success_market,
        "commodity": commodity,
        "data": market_data if market_data else [],
        "distance_km": distance
    }
    
    # Add latest prices information if data was found
    if market_data and len(market_data) > 0:
        latest_record = sorted(
            market_data,
            key=lambda x: datetime.datetime.strptime(x.get("Price Date", "01 Jan 2000"), "%d %b %Y"),
            reverse=True
        )[0]
        
        result["latest_price"] = {
            "min_price": float(latest_record.get("Min Price", "0")),
            "max_price": float(latest_record.get("Max Price", "0")),
            "modal_price": float(latest_record.get("Modal Price", "0")),
            "date": latest_record.get("Price Date", "Unknown"),
            "variety": latest_record.get("Variety", "Unknown")
        }
        
        if debug:
            print(f"\nSuccessfully found data for {commodity} in {success_market}, {state}:")
            print(f"- Number of records: {len(market_data)}")
            print(f"- Latest price: ₹{result['latest_price']['modal_price']} (Min: ₹{result['latest_price']['min_price']}, Max: ₹{result['latest_price']['max_price']})")
            print(f"- Date: {result['latest_price']['date']}")
            print(f"- Variety: {result['latest_price']['variety']}")
    else:
        result["error"] = f"No data found for {commodity} in {state}"
        
        if debug:
            print(f"\nNo data found for {commodity} in any market in {state}")
    
    return result

if __name__ == "__main__":
    # Test coordinates for Chandigarh area
    test_lat = 30.7463
    test_lon = 76.6469
    test_commodity = "Rice"
    debug_mode = True
    
    result = get_commodity_prices_by_location(test_lat, test_lon, test_commodity, debug=debug_mode)
    
    if debug_mode:
        print("\nTest completed successfully!")
