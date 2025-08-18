# Market Database and Location-Based Services

This directory implements a comprehensive market database and geolocation services for the Farmora AI Server.

## Features

1. **Market Database Builder**
   - Scrapes all states, districts, markets, and commodities from Agmarknet
   - Stores data in a local JSON database
   - Provides geocoded coordinates for markets

2. **Enhanced Geolocation Services**
   - Reverse geocoding with offline fallback
   - District name normalization
   - Nearest market finder based on coordinates

3. **Location-Based Commodity Price Lookup**
   - Find nearest markets based on coordinates
   - Get commodity prices from the most appropriate market

4. **Clean Code & Production Ready**
   - Optimized for production use without debug statements
   - Error handling with graceful fallbacks
   - Well-documented functions with type hints

## Usage

### Building the Market Database
```python
from tools.market_database_builder import scrape_all_market_data

# This will scrape all market data and create the database
market_data = scrape_all_market_data()
```

### Finding Nearest Markets by Coordinates
```python
from tools.geo_utils import find_markets_by_coordinates

# Find markets near Mohali, Punjab
markets = find_markets_by_coordinates(30.7463, 76.6469, "rice")
print(markets)  # ['Sri Har Gobindpur', 'Kharar', 'Mohali']
```

### Getting Commodity Prices by Location
```python
from tools.scrape_commodity import scrape_commodity_by_location

# Get rice prices near Mohali, Punjab
results = scrape_commodity_by_location(
    lat=30.7463, 
    lon=76.6469,
    commodity="rice"
)
print(results["latest_prices"])
```

## Files

- `market_database_builder.py` - Scrapes and builds the market database
- `geo_utils.py` - Provides geolocation utilities
- `scrape_commodity.py` - Gets commodity prices with location support

## Data Files

- `data/markets_database.json` - Contains all market data
- `data/geocoded_markets.json` - Contains market coordinates

## Notes

The system uses a fallback approach:
1. First tries to use the market database if available
2. If not found, falls back to online geocoding services
3. If online services fail, uses hardcoded location data

This ensures the system works reliably even with limited connectivity.

## Recent Updates

- **Code Cleanup (2023-04-10)**: Removed debug print statements and improved code readability
- **Error Handling**: Improved error handling with silent failure and appropriate fallbacks
- **Performance**: Reduced unnecessary operations and improved code efficiency
