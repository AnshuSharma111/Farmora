"""
Farmora Market Database Setup Script

This script initializes the market database by creating the necessary data directory
and running the market database builder if needed.

It's designed to be run once during initial setup or when the database needs to be refreshed.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tools.market_database_builder import scrape_all_market_data, geocode_markets, MARKETS_FILE, GEOCODED_MARKETS_FILE, DATA_DIR

def setup_market_database(force_rebuild=False):
    """
    Set up the market database and ensure all required files are present.
    
    Args:
        force_rebuild: If True, rebuilds the database even if it already exists
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    needs_rebuild = force_rebuild or not os.path.exists(MARKETS_FILE)
    needs_geocoding = force_rebuild or not os.path.exists(GEOCODED_MARKETS_FILE)
    
    # Build or rebuild the market database if needed
    market_data = None
    if needs_rebuild:
        print("Building market database...")
        market_data = scrape_all_market_data()
        if market_data:
            print(f"Market database created at {MARKETS_FILE}")
        else:
            print("Failed to build market database")
            return False
    
    # Geocode the markets if needed
    if needs_geocoding:
        if not market_data:
            # Load existing market data if we didn't already build it
            try:
                with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
                    import json
                    market_data = json.load(f)
            except Exception as e:
                print(f"Failed to load market data: {e}")
                return False
                
        print("Geocoding markets...")
        geocoded_markets = geocode_markets(market_data)
        if geocoded_markets:
            print(f"Geocoded markets database created at {GEOCODED_MARKETS_FILE}")
        else:
            print("Failed to geocode markets")
            return False
    
    print("Market database setup complete!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up the Farmora market database")
    parser.add_argument("--force", action="store_true", help="Force rebuild of the database")
    args = parser.parse_args()
    
    if setup_market_database(force_rebuild=args.force):
        print("Setup completed successfully")
    else:
        print("Setup failed")
        sys.exit(1)
