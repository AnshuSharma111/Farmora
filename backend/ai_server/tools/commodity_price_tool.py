"""
Commodity Price Lookup Tool

This module provides functions to scrape commodity prices from agricultural markets
based on user location (latitude and longitude). It consolidates the functionality
from the original scrape_commodity.py and enhanced_commodity_lookup.py into a single tool.
"""

import time
import json
import os
import math
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Define paths to data files
DATA_DIR = Path(__file__).parent.parent / "data"
DISTRICTS_FILE = DATA_DIR / "districts_database.json"
MARKETS_FILE = DATA_DIR / "markets_database.json"

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the distance between two coordinates in kilometers using the Haversine formula.
    
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

def find_nearest_location(lat: float, lon: float) -> Dict[str, Any]:
    """
    Find the nearest district and state based on user coordinates.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        Dictionary with state, district, and distance information
    """
    # Create districts database file if it doesn't exist (simplified version)
    if not os.path.exists(DISTRICTS_FILE):
        return {"state": "Punjab", "district": "Ludhiana", "distance": 0}
    
    # Load district coordinates database
    try:
        with open(DISTRICTS_FILE, 'r') as f:
            districts_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"state": "Punjab", "district": "Ludhiana", "distance": 0}
    
    # Find nearest district
    nearest_district = None
    min_distance = float('inf')
    
    for district_entry in districts_data:
        dist_lat = district_entry.get("latitude")
        dist_lon = district_entry.get("longitude")
        
        if not (dist_lat and dist_lon):
            continue
            
        distance = haversine_distance((lat, lon), (dist_lat, dist_lon))
        
        if distance < min_distance:
            min_distance = distance
            nearest_district = district_entry
    
    if nearest_district:
        return {
            "state": nearest_district.get("state", "Punjab"),
            "district": nearest_district.get("district", "Ludhiana"),
            "distance": min_distance
        }
    else:
        return {"state": "Punjab", "district": "Ludhiana", "distance": 0}

def get_markets_in_district(state: str, district: str) -> List[str]:
    """
    Get all markets in a specific district.
    
    Args:
        state: State name
        district: District name
        
    Returns:
        List of market names in the district
    """
    # Create markets database file if it doesn't exist (simplified version)
    if not os.path.exists(MARKETS_FILE):
        return ["Ludhiana"]  # Default fallback
    
    # Load markets database
    try:
        with open(MARKETS_FILE, 'r') as f:
            markets_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return ["Ludhiana"]  # Default fallback
    
    # Extract markets for the specified district
    district_markets = []
    
    for market_entry in markets_data:
        if market_entry.get("state") == state and market_entry.get("district") == district:
            district_markets.append(market_entry.get("market"))
    
    return district_markets if district_markets else ["Ludhiana"]

def get_alternate_markets(state: str) -> List[Dict[str, str]]:
    """
    Get a list of alternative major markets in the state.
    
    Args:
        state: State name
        
    Returns:
        List of dictionaries with market information
    """
    # Map of states to their major agricultural markets
    state_markets = {
        "Punjab": [
            {"district": "Ludhiana", "market": "Ludhiana"},
            {"district": "Amritsar", "market": "Amritsar"},
            {"district": "Patiala", "market": "Patiala"},
            {"district": "Jalandhar", "market": "Jalandhar"},
            {"district": "Bathinda", "market": "Bathinda"}
        ],
        "Haryana": [
            {"district": "Karnal", "market": "Karnal"},
            {"district": "Ambala", "market": "Ambala"},
            {"district": "Hisar", "market": "Hisar"},
            {"district": "Gurugram", "market": "Gurugram"},
            {"district": "Kurukshetra", "market": "Kurukshetra"}
        ],
        "Uttar Pradesh": [
            {"district": "Lucknow", "market": "Lucknow"},
            {"district": "Kanpur", "market": "Kanpur"},
            {"district": "Varanasi", "market": "Varanasi"},
            {"district": "Agra", "market": "Agra"},
            {"district": "Meerut", "market": "Meerut"}
        ],
        "Himachal Pradesh": [
            {"district": "Shimla", "market": "Shimla"},
            {"district": "Solan", "market": "Solan"},
            {"district": "Kangra", "market": "Dharamshala"},
            {"district": "Kullu", "market": "Kullu"},
            {"district": "Mandi", "market": "Mandi"}
        ]
    }
    
    # Return markets for the specified state or a default list
    return state_markets.get(state, [{"district": "Ludhiana", "market": "Ludhiana"}])

def scrape_commodity(
    state: str,
    district: str,
    market: str,
    commodity: str,
    price_arrival: str = "Both",
    date_from: str = None,
    date_to: str = None,
    debug: bool = False
) -> List[Dict[str, str]]:
    """
    Scrapes commodity price and arrival data from the Agmarknet website.
    
    Args:
        state: The state name (e.g., "Himachal Pradesh")
        district: The district name (e.g., "Shimla")
        market: The market name (e.g., "Shimla")
        commodity: The commodity name (e.g., "Apple")
        price_arrival: Type of data to fetch - "Price", "Arrival", or "Both" (default)
        date_from: Start date in format "dd-MMM-yyyy" (e.g., "27-Jul-2023")
                   If not provided, defaults to 7 days ago
        date_to: End date in format "dd-MMM-yyyy" (e.g., "18-Aug-2023")
                 If not provided, defaults to current date
        debug: If True, enables debug mode with extra logging and screenshots
    
    Returns:
        A list of dictionaries containing the scraped data with keys such as:
        - State Name
        - District Name
        - Market Name
        - Variety
        - Grade
        - Min Price
        - Max Price
        - Modal Price
        - Price Date
    """
    def take_debug_screenshot(name):
        """Take a screenshot if debug mode is on"""
        if debug:
            screenshot_path = os.path.join(DATA_DIR, f"debug_{name}.png")
            driver.save_screenshot(screenshot_path)
            if debug:
                print(f"[DEBUG] Screenshot saved as: {screenshot_path}")
            
    def debug_print(message):
        """Print a message if debug mode is on"""
        if debug:
            print(f"[DEBUG] {message}")
            
    # Create headless or non-headless browser based on debug setting
    chrome_options = Options()
    if not debug:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
            
    initial_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    debug_print(f"Opening {initial_url}")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(initial_url)
        take_debug_screenshot("scrape_initial")

        # Select Price/Arrivals
        try:
            debug_print("Selecting price/arrival type: " + price_arrival)
            dropdown = Select(driver.find_element("id", 'ddlArrivalPrice'))
            options = [o.text for o in dropdown.options]
            if debug:
                print("Available price/arrival options:")
                for o in options:
                    print(f"  - {o}")
            
            dropdown.select_by_visible_text(price_arrival)
            time.sleep(2)
            take_debug_screenshot("after_pricetype")
        except Exception as e:
            debug_print(f"Error selecting Price/Arrival type: {e}")
            driver.quit()
            raise ValueError(f"Price/Arrival option '{price_arrival}' not found in dropdown.")

        # Select commodity
        try:
            debug_print("Selecting commodity: " + commodity)
            dropdown = Select(driver.find_element("id", 'ddlCommodity'))
            options = [o.text for o in dropdown.options]
            if debug:
                print("Available commodities (first 10):")
                for o in options[:10]:
                    print(f"  - {o}")
                    
            dropdown.select_by_visible_text(commodity)
            time.sleep(2)
            take_debug_screenshot("after_commodity")
        except Exception as e:
            debug_print(f"Error selecting Commodity: {e}")
            driver.quit()
            raise ValueError(f"Commodity '{commodity}' not found in dropdown.")

        # Select state
        try:
            debug_print("Selecting state: " + state)
            dropdown = Select(driver.find_element("id", 'ddlState'))
            options = [o.text for o in dropdown.options]
            if debug:
                print("Available states (first 10):")
                for o in options[:10]:
                    print(f"  - {o}")
            
            dropdown.select_by_visible_text(state)
            time.sleep(2)
            take_debug_screenshot("after_state")
        except Exception as e:
            debug_print(f"Error selecting State: {e}")
            driver.quit()
            raise ValueError(f"State '{state}' not found in dropdown.")

        # Wait for district dropdown to update
        try:
            debug_print("Selecting district: " + district)
            WebDriverWait(driver, 10).until(
                lambda d: len(Select(d.find_element("id", 'ddlDistrict')).options) > 1
            )
            
            dropdown = Select(driver.find_element("id", 'ddlDistrict'))
            if debug:
                print("Waiting for district dropdown to update...")
                time.sleep(2)  # Extra delay for stability
                options = [o.text for o in dropdown.options if o.text != "--Select--"]
                print("Available districts:")
                for o in options:
                    print(f"  - {o}")
            
            # Try exact match first
            try:
                dropdown.select_by_visible_text(district)
            except Exception as e:
                debug_print(f"Exact match failed for district: {e}")
                
                # Try case-insensitive match
                options = [o.text for o in dropdown.options if o.text != "--Select--"]
                match_found = False
                
                for option_text in options:
                    if district.lower() == option_text.lower() or district.lower() in option_text.lower():
                        debug_print(f"Found close match for district: '{option_text}' for '{district}'")
                        dropdown.select_by_visible_text(option_text)
                        district = option_text  # Update the district name
                        match_found = True
                        break
                        
                if not match_found:
                    # If no match, select the first valid option
                    if len(options) > 0:
                        first_option = options[0]
                        debug_print(f"No match found for district '{district}', using first available: {first_option}")
                        dropdown.select_by_visible_text(first_option)
                        district = first_option  # Update the district name
                    else:
                        raise ValueError(f"No valid district options available")
                
            time.sleep(3)  # Extended wait time to ensure market dropdown updates
            take_debug_screenshot("after_district")
        except Exception as e:
            debug_print(f"Error selecting District: {e}")
            driver.quit()
            raise ValueError(f"District '{district}' not found in dropdown after waiting: {str(e)}")

        # Select market with flexible matching
        try:
            debug_print("Selecting market: " + market)
            WebDriverWait(driver, 10).until(
                lambda d: len(Select(d.find_element("id", 'ddlMarket')).options) > 1
            )
            
            dropdown = Select(driver.find_element("id", 'ddlMarket'))
            if debug:
                print("Waiting for market dropdown to update...")
                time.sleep(2)  # Extra delay for stability
                options = [o.text for o in dropdown.options if o.text != "--Select--"]
                print("Available markets:")
                for o in options:
                    print(f"  - {o}")
                    
            # Filter out "--Select--" option
            market_options = [option.text for option in dropdown.options if option.text != "--Select--"]
            
            if not market_options:
                debug_print(f"No valid market options available for district {district}")
                raise ValueError(f"No valid market options available for district {district}")
                
            # Try exact match first
            try:
                dropdown.select_by_visible_text(market)
                debug_print("Selected market (exact match)")
            except:
                # If exact match fails, try a more flexible approach
                # Try to find a close match ignoring case
                match_found = False
                for option_text in market_options:
                    if market.lower() == option_text.lower() or market.lower() in option_text.lower():
                        debug_print(f"Found close match: '{option_text}' for '{market}'")
                        dropdown.select_by_visible_text(option_text)
                        match_found = True
                        break
                        
                if not match_found:
                    # Use the first available market as fallback
                    first_market = market_options[0]
                    dropdown.select_by_visible_text(first_market)
                    debug_print(f"No match found for market '{market}', using first available: {first_market}")
                    market = first_market  # Update the market name
                        
            time.sleep(2)
            take_debug_screenshot("after_market")
        except Exception as e:
            debug_print(f"Error selecting Market: {e}")
            driver.quit()
            raise ValueError(f"Market selection failed: {str(e)}")

        # Set Date From and Date To
        today = datetime.now()
        # Use a safer date range format that the website accepts (14 days ago to today)
        # Agmarknet uses a specific format with abbreviated month name
        default_from = (today - timedelta(days=14)).strftime('%d-%b-%Y')
        default_to = today.strftime('%d-%b-%Y')
        
        # Start with current year first (or a reasonable year that likely has data)
        # If we're in a future test environment (2025+), use 2023 data
        if today.year >= 2025:
            default_from = default_from.replace(str(today.year), "2023")
            default_to = default_to.replace(str(today.year), "2023")
        
        date_from_val = date_from if date_from else default_from
        date_to_val = date_to if date_to else default_to
        
        try:
            debug_print(f"Setting date range from {date_from_val} to {date_to_val}")
            
            # Clear and set the from date with more robust approach
            date_input_from = driver.find_element(By.ID, "txtDate")
            date_input_from.clear()
            time.sleep(1)  # Give time for field to clear
            # Send date character by character with brief pauses
            for char in date_from_val:
                date_input_from.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)
            
            # Clear and set the to date with more robust approach
            date_input_to = driver.find_element(By.ID, "txtDateTo")
            date_input_to.clear()
            time.sleep(1)  # Give time for field to clear
            # Send date character by character with brief pauses
            for char in date_to_val:
                date_input_to.send_keys(char)
                time.sleep(0.1)
            time.sleep(2)
            
            take_debug_screenshot("after_dates")
        except Exception as e:
            debug_print(f"Error setting dates: {e}")
            driver.quit()
            raise RuntimeError(f"Date input fields not found. Error: {str(e)}")

        # Click Go button with retry mechanism for common click intercept issues
        max_retries = 5
        for retry in range(max_retries):
            try:
                debug_print("Clicking Go button")
                button = driver.find_element("id", 'btnGo')
                
                # Try to scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                
                # First try: JavaScript click which can bypass some intercepted click issues
                driver.execute_script("arguments[0].click();", button)
                debug_print("Go button clicked (using JS)")
                time.sleep(3)
                take_debug_screenshot("after_go")
                break
            except Exception as e:
                debug_print(f"Error clicking Go button (attempt {retry+1} with JS): {e}")
                
                try:
                    # Second approach: Try to handle any validation errors
                    # Look for and dismiss any validation messages
                    try:
                        error_messages = driver.find_elements(By.CSS_SELECTOR, "div.ajax__validatorcallout")
                        if error_messages:
                            debug_print(f"Found {len(error_messages)} validation errors, attempting to dismiss")
                            for msg in error_messages:
                                try:
                                    # Try to click the close button on each error
                                    close_btn = msg.find_element(By.CSS_SELECTOR, "div.ajax__validatorcallout_close_button_cell")
                                    driver.execute_script("arguments[0].click();", close_btn)
                                except:
                                    pass
                    except:
                        pass
                    
                    # Try clicking with Actions (another way to bypass intercepts)
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    debug_print("Go button clicked (using Actions)")
                    time.sleep(3)
                    take_debug_screenshot("after_go_actions")
                    break
                except Exception as e2:
                    debug_print(f"Error clicking Go button (attempt {retry+1} with Actions): {e2}")
                    
                if retry == max_retries - 1:
                    # On last retry, try a desperate approach - direct form submission
                    try:
                        driver.execute_script("document.forms[0].submit();")
                        debug_print("Attempted form submission directly")
                        time.sleep(3)
                        take_debug_screenshot("after_form_submit")
                        break
                    except Exception as e3:
                        debug_print(f"Error submitting form: {e3}")
                        # On last retry, take screenshot and raise error
                        take_debug_screenshot("error_button")
                        driver.quit()
                        raise RuntimeError(f"Go button click failed after {max_retries} attempts: {str(e)}")
                        
                time.sleep(2)  # Wait before retry

        # Wait for the table to be present
        debug_print("Waiting for results table...")
        try:
            # Try different table IDs
            table_ids = ['cphBody_GridViewBoth', 'cphBody_GridPriceData', 'cphBody_GridArrivalData']
            table_found = False
            table_id = None
            
            # First try with explicit IDs
            for tid in table_ids:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, tid))
                    )
                    table_found = True
                    table_id = tid
                    debug_print(f"Table found with ID: {tid}")
                    break
                except:
                    continue
            
            # If no table found by ID, try to find any table with results data
            if not table_found:
                debug_print("No table found by ID, searching for table with results data...")
                try:
                    # Look for table header with expected column names
                    header_xpath = "//table//tr/th[contains(text(), 'State Name') or contains(text(), 'Market Name')]"
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, header_xpath))
                    )
                    
                    # Find the containing table
                    table_element = driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'State Name')]]")
                    if table_element:
                        table_found = True
                        table_id = table_element.get_attribute("id")
                        if not table_id:
                            # Use a generic identifier if no ID is available
                            table_id = "results_table"
                        debug_print(f"Table found by content search, using ID: {table_id}")
                except:
                    debug_print("No results table found by content search")
            
            if not table_found:
                debug_print("No data table found on the page")
                take_debug_screenshot("table_not_found")
                raise RuntimeError("No data table found on the page")
                
            # Process table data
            debug_print("Table found! Processing data...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # If we have a specific table ID, try to find it
            if table_id != "results_table":
                table = soup.find('table', id=table_id)
            else:
                # If we're using the generic ID, find by content
                debug_print("Finding table by content...")
                # Look for table with the characteristic header
                tables = soup.find_all('table')
                table = None
                for t in tables:
                    headers = t.find_all('th')
                    header_texts = [h.get_text().strip() for h in headers]
                    if any('State Name' in h for h in header_texts) or any('Market Name' in h for h in header_texts):
                        table = t
                        debug_print("Table found by content search")
                        break
            
            if not table:
                debug_print(f"Table with data not found in the page source")
                raise RuntimeError(f"Table with data not found in the page source")
                
            jsonList = []
            
            # Extract table headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text().strip() for th in header_row.find_all('th')]
                
            # Process data rows (skip header row and summary rows)
            for row in table.find_all('tr')[1:]:  # Skip header row
                # Skip summary rows (they have a different background color)
                if 'background-color:#F9F9F9' in str(row):
                    continue
                    
                cells = row.find_all('td')
                if cells:
                    # Use the actual headers from the table for the keys
                    data = {}
                    for i, header in enumerate(headers):
                        if i < len(cells):
                            # Clean up header name for use as a key
                            clean_header = header.split('(')[0].strip()  # Remove units in parentheses
                            data[clean_header] = cells[i].get_text().strip()
                    jsonList.append(data)
            
            debug_print(f"Processed {len(jsonList)} records.")
            return jsonList
            
        except Exception as e:
            debug_print(f"Error processing table data: {e}")
            take_debug_screenshot("error_processing")
            raise RuntimeError(f"Error processing table data: {str(e)}")
    finally:
        driver.quit()

def get_latest_prices(data: List[Dict[str, str]], commodity_variety: Optional[str] = None) -> Dict[str, Union[str, float]]:
    """
    Extract the most recent price information for a specific commodity variety
    
    Args:
        data: List of dictionaries containing scraped data
        commodity_variety: Optional variety of the commodity to filter by (e.g., "Royal Delicious")
                           If not provided, will use the most recent entry regardless of variety
                           
    Returns:
        Dictionary with the latest price information including:
        - variety: The variety of the commodity
        - min_price: Minimum price
        - max_price: Maximum price
        - modal_price: Modal (most common) price
        - date: Date of the price record
        - market: Market name
    """
    # Handle empty data
    if not data:
        return {}
    
    # Filter by variety if specified
    filtered_data = data
    if commodity_variety:
        filtered_data = [item for item in data if item.get('Variety') == commodity_variety]
    
    if not filtered_data:
        return {}
    
    # Sort by date (most recent first)
    try:
        # Try to handle different date formats
        sorted_data = sorted(
            filtered_data, 
            key=lambda x: datetime.strptime(
                x.get('Price Date', x.get('Reported Date', '01 Jan 2000')), 
                '%d %b %Y'
            ),
            reverse=True
        )
    except ValueError:
        # If date parsing fails, just use the first entry
        sorted_data = filtered_data
    
    latest = sorted_data[0]
    
    # Return formatted result
    return {
        'variety': latest.get('Variety', 'Unknown'),
        'min_price': float(latest.get('Min Price', '0')),
        'max_price': float(latest.get('Max Price', '0')),
        'modal_price': float(latest.get('Modal Price', '0')),
        'date': latest.get('Price Date', latest.get('Reported Date', 'Unknown')),
        'market': latest.get('Market Name', 'Unknown')
    }

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
                    "harvesting_period": "Data not available",
                    "expected_next_harvest": "Data not available"
                }
            }
    
    return results

def get_commodity_price(lat: float, lon: float, commodity: str, debug: bool = False) -> Dict[str, Any]:
    """
    Main function to get commodity prices based on user location.
    This is the primary function to be called from the pipeline.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodity: The commodity name to look up (e.g., "Rice", "Wheat")
        debug: Whether to enable debug mode
        
    Returns:
        Dictionary with price data formatted for the pipeline:
        - state: Determined state name
        - district: Determined district name
        - market: Market name used
        - latest_prices: Dictionary with price info (min_price, max_price, modal_price, date, variety)
        - error: Error message if any occurred (only present if an error occurred)
    """
    result = {
        "state": None,
        "district": None,
        "market": None,
        "latest_prices": {},
        "data_points": 0
    }
    
    try:
        # Step 1: Find the nearest location based on coordinates
        location_info = find_nearest_location(lat, lon)
        state = location_info["state"]
        district = location_info["district"]
        
        if debug:
            print(f"Found nearest location: {district}, {state} ({location_info['distance']:.2f} km)")
        
        result["state"] = state
        result["district"] = district
        
        # Step 2: Get potential markets for the district
        markets = get_markets_in_district(state, district)
        
        if not markets:
            if debug:
                print(f"No markets found for {district}, {state}. Using default markets.")
            markets = ["Ludhiana"]
        
        # Step 3: Try to get data for each market until we find one with results
        market_data = []
        successful_market = None
        
        # Set date range (2 weeks ago to today)
        today = datetime.now()
        two_weeks_ago = today - timedelta(days=14)
        date_from = two_weeks_ago.strftime('%d-%b-%Y')
        date_to = today.strftime('%d-%b-%Y')
        
        # Try each market in the district
        for market in markets:
            try:
                if debug:
                    print(f"Trying to get data for {commodity} from {market} market in {district}, {state}")
                
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
                    successful_market = market
                    if debug:
                        print(f"Successfully found data in {market} market")
                    break
            except Exception as e:
                if debug:
                    print(f"Error getting data from {market} market: {str(e)}")
                continue
        
        # If still no data, try alternate markets in the state
        if not market_data or len(market_data) == 0:
            if debug:
                print(f"No data found in any market in {district}. Trying alternate markets in {state}.")
            
            alternate_markets = get_alternate_markets(state)
            
            for market_info in alternate_markets:
                alt_district = market_info["district"]
                alt_market = market_info["market"]
                
                # Skip if we already tried this market
                if alt_district == district and alt_market in markets:
                    continue
                
                try:
                    if debug:
                        print(f"Trying alternate market: {alt_market} in {alt_district}, {state}")
                    
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
                        successful_market = alt_market
                        district = alt_district  # Update district to match the market
                        result["district"] = district
                        if debug:
                            print(f"Successfully found data in alternate market {alt_market}")
                        break
                except Exception as e:
                    if debug:
                        print(f"Error getting data from alternate market {alt_market}: {str(e)}")
                    continue
        
        # Step 4: Process the results
        if successful_market and market_data:
            result["market"] = successful_market
            result["data_points"] = len(market_data)
            latest_prices = get_latest_prices(market_data)
            result["latest_prices"] = latest_prices
            
            if debug:
                print(f"Successfully found price data for {commodity} in {successful_market}, {state}")
                print(f"Latest price: ₹{latest_prices.get('modal_price')} (₹{latest_prices.get('min_price')} - ₹{latest_prices.get('max_price')})")
                print(f"Variety: {latest_prices.get('variety')}")
                print(f"Date: {latest_prices.get('date')}")
        else:
            result["error"] = f"No price data found for {commodity} in any market in {state}"
            if debug:
                print(result["error"])
    
    except Exception as e:
        result["error"] = str(e)
        if debug:
            print(f"Error in get_commodity_price: {str(e)}")
    
    return result

def get_crop_seasons(commodity: str) -> Dict[str, str]:
    """
    Get seasonal information for a crop.
    
    Args:
        commodity: The crop name
        
    Returns:
        Dictionary with seasonal information
    """
    # Common crop seasons in India
    CROP_SEASONS = {
        "rice": {
            "growing_season": "Kharif (June-July to October-November)",
            "harvesting_period": "September-December",
            "expected_next_harvest": "October-November"
        },
        "wheat": {
            "growing_season": "Rabi (October-December to March-April)",
            "harvesting_period": "February-May", 
            "expected_next_harvest": "March-April"
        },
        "maize": {
            "growing_season": "Both Kharif and Rabi seasons",
            "harvesting_period": "September-October (Kharif), February-March (Rabi)",
            "expected_next_harvest": "Varies by region"
        },
        "potato": {
            "growing_season": "Rabi (October-November to February-March)",
            "harvesting_period": "January-March",
            "expected_next_harvest": "January-February"
        },
        "onion": {
            "growing_season": "Kharif, late Kharif, and Rabi",
            "harvesting_period": "Year-round in different regions",
            "expected_next_harvest": "Varies by region"
        },
        "tomato": {
            "growing_season": "Year-round in different regions",
            "harvesting_period": "Varies by region",
            "expected_next_harvest": "Varies by region"
        },
        "apple": {
            "growing_season": "Spring (March-April)",
            "harvesting_period": "July-October",
            "expected_next_harvest": "August-September"
        },
        "strawberry": {
            "growing_season": "October-November",
            "harvesting_period": "January-March",
            "expected_next_harvest": "January-February"
        }
        # Add more crops as needed
    }
    
    return CROP_SEASONS.get(commodity.lower(), {})

def get_all_commodity_prices(lat: float, lon: float, commodities: List[str], debug: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Get price data for multiple commodities based on location.
    This is the function that should be called from the processing pipeline.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodities: List of commodity names to lookup
        debug: Whether to enable debug mode
        
    Returns:
        Dictionary mapping each commodity to its price data
    """
    result = {}
    
    # If no commodities specified, use default commodities
    if not commodities:
        commodities = ["Rice", "Wheat"]
    
    # Process each commodity
    for commodity in commodities:
        try:
            if debug:
                print(f"Getting price data for {commodity} at coordinates {lat}, {lon}")
                
            commodity_data = get_commodity_price(lat, lon, commodity, debug=debug)
            
            # Add seasonal information if available
            seasons = get_crop_seasons(commodity)
            if seasons:
                commodity_data["seasonal_info"] = seasons
                
            result[commodity] = commodity_data
        except Exception as e:
            result[commodity] = {
                "error": str(e),
                "seasonal_info": get_crop_seasons(commodity)  # Add seasonal info even if price lookup fails
            }
    
    return result

if __name__ == "__main__":
    # Test the function with coordinates near Punjab
    test_lat = 30.7463
    test_lon = 76.6469
    test_commodity = "Rice"
    
    print(f"Testing commodity price lookup for {test_commodity} at {test_lat}, {test_lon}")
    result = get_commodity_price(test_lat, test_lon, test_commodity, debug=True)
    
    if "error" not in result:
        print("\nResults summary:")
        print(f"State: {result['state']}")
        print(f"District: {result['district']}")
        print(f"Market: {result['market']}")
        print(f"Price: ₹{result['latest_prices'].get('modal_price')}")
        print(f"Date: {result['latest_prices'].get('date')}")
        print(f"Variety: {result['latest_prices'].get('variety')}")
    else:
        print(f"\nError: {result['error']}")
        
    print("\nTest complete!")
