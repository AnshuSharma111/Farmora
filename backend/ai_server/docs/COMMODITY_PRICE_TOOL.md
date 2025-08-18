# Commodity Price Tool Documentation

## Overview
The Commodity Price Tool provides functionality to retrieve agricultural commodity prices from Indian markets based on geographical location. It uses web scraping techniques to fetch price data from the Agmarknet website, which is the official agricultural market information system of India.

## Features

- Location-based price data retrieval
- Support for multiple commodities
- Robust error handling and fallback mechanisms
- Intelligent market selection based on proximity
- Detailed price information including min/max/modal prices
- Seasonal crop information for when price data isn't available
- District name normalization (e.g., Hisar/Hissar, Gurugram/Gurgaon)

## Prerequisites

The tool requires the following Python packages:

```
selenium
beautifulsoup4
requests
geopy
pandas
```

Additionally, you'll need Chrome and ChromeDriver installed for the web scraping functionality.

## Usage

### Basic Usage

```python
from tools.commodity_price_tool import get_commodity_price

# Get price data for a specific commodity based on coordinates
lat = 30.7463  # Latitude
lon = 76.6469  # Longitude
commodity = "Rice"

result = get_commodity_price(lat, lon, commodity)

# Check for errors
if "error" not in result:
    print(f"Found price data for {commodity} in {result['market']}")
    print(f"Latest price: ₹{result['latest_prices']['modal_price']}")
    print(f"Date: {result['latest_prices']['date']}")
    print(f"Variety: {result['latest_prices']['variety']}")
else:
    print(f"Error: {result['error']}")
    
    # Even if price data isn't available, seasonal information might be
    if "seasonal_info" in result:
        print(f"Growing Season: {result['seasonal_info']['growing_season']}")
        print(f"Harvesting Period: {result['seasonal_info']['harvesting_period']}")
```

### Multiple Commodities

```python
from tools.commodity_price_tool import get_all_commodity_prices

# Get price data for multiple commodities
lat = 30.7463  # Latitude
lon = 76.6469  # Longitude
commodities = ["Rice", "Wheat", "Potato"]

results = get_all_commodity_prices(lat, lon, commodities)

# Process results
for commodity, data in results.items():
    if "error" not in data:
        print(f"{commodity}: ₹{data['latest_prices']['modal_price']} in {data['market']}")
    else:
        print(f"{commodity}: {data['error']}")
        
        # Show seasonal info if available
        if "seasonal_info" in data:
            print(f"  Growing Season: {data['seasonal_info']['growing_season']}")
            print(f"  Next Harvest: {data['seasonal_info']['expected_next_harvest']}")
```

## API Reference

### `get_commodity_price(lat, lon, commodity, debug=False)`

Retrieves price data for a specific commodity based on user location.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate
- `commodity` (str): The commodity name to look up (e.g., "Rice", "Wheat")
- `debug` (bool, optional): Whether to print debug info and save debug screenshots. Defaults to False.

**Returns:**
Dictionary with price data formatted for the pipeline:
- `state`: Determined state name
- `district`: Determined district name
- `market`: Market name used
- `latest_prices`: Dictionary with price info (min_price, max_price, modal_price, date, variety)
- `data_points`: Number of records found
- `seasonal_info`: Dictionary with seasonal information (growing_season, harvesting_period, expected_next_harvest)
- `error`: Error message if any occurred (only present if an error occurred)

### `get_all_commodity_prices(lat, lon, commodities, debug=False)`

Gets price data for multiple commodities based on location.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate
- `commodities` (List[str]): List of commodity names to look up
- `debug` (bool, optional): Whether to print debug info and save debug screenshots. Defaults to False.

**Returns:**
Dictionary mapping each commodity name to its price data results (same format as `get_commodity_price`).

### `get_crop_seasons(commodity)`

Gets seasonal information for a specific crop.

**Parameters:**
- `commodity` (str): The crop name to look up

**Returns:**
Dictionary with seasonal information:
- `growing_season`: The typical growing season for the crop
- `harvesting_period`: When the crop is typically harvested
- `expected_next_harvest`: When the next harvest is expected

## Error Handling

The tool implements several layers of error handling:

1. **Market fallbacks**: If data isn't found in the nearest market, the tool tries alternate markets in the same district and state.
2. **State fallbacks**: If no data is found in the nearest state, the tool tries major markets in neighboring states.
3. **Date range adjustments**: If no data is found for the current date range, the tool tries with older date ranges.
4. **Browser automation recovery**: The tool handles various browser automation challenges with retries and fallbacks.
5. **Name normalization**: Handles district name variations (Hisar/Hissar, Gurugram/Gurgaon) for better matching.
6. **Seasonal fallbacks**: Provides seasonal crop information when price data isn't available.

## Screenshots

When debug mode is enabled, the tool saves screenshots at various stages of the scraping process to help diagnose issues. These are saved in the `data` directory with filenames like `debug_scrape_initial.png`, `debug_after_go.png`, etc.
