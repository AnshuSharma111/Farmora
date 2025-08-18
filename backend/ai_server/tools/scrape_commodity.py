import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional, Union, Tuple, Any
from .geo_utils import (
    get_state_district, get_nearest_markets, get_common_crops,
    find_markets_by_coordinates, get_nearest_location_from_database
)

def scrape_commodity(
    state: str,
    commodity: str,
    district: str,
    market: str,
    price_arrival: str = "Both",  # "Price", "Arrival", or "Both"
    date_from: str = None,         # e.g., "27-Jul-2025"
    date_to: str = None,           # e.g., "18-Aug-2025"
    debug: bool = False            # Enable debug mode
) -> List[Dict[str, str]]:
    """
    Scrapes commodity price and arrival data from the Agmarknet website.
    
    Args:
        state: The state name (e.g., "Himachal Pradesh")
        commodity: The commodity name (e.g., "Apple")
        district: The district name (e.g., "Shimla")
        market: The market name (e.g., "Shimla and Kinnaur(Nerwa)")
        price_arrival: Type of data to fetch - "Price", "Arrival", or "Both" (default)
        date_from: Start date in format "dd-MMM-yyyy" (e.g., "27-Jul-2025")
                   If not provided, defaults to 7 days ago
        date_to: End date in format "dd-MMM-yyyy" (e.g., "18-Aug-2025")
                 If not provided, defaults to current date
        debug: If True, enables debug mode with extra logging and screenshots
    
    Returns:
        A list of dictionaries containing the scraped data with keys such as:
        - State Name
        - District Name
        - Market Name
        - Variety
        - Group
        - Arrivals (quantity)
        - Min Price
        - Max Price
        - Modal Price
        - Reported Date
        - Grade
    
    Example:
        >>> results = scrape_commodity(
        ...     "Himachal Pradesh", 
        ...     "Apple", 
        ...     "Shimla", 
        ...     "Shimla and Kinnaur(Nerwa)"
        ... )
    """
    def take_debug_screenshot(name):
        """Take a screenshot if debug mode is on"""
        if debug:
            screenshot_path = f"debug_{name}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"DEBUG: Screenshot saved to {screenshot_path}")
            
    def debug_print(message):
        """Print a message if debug mode is on"""
        if debug:
            print(f"DEBUG: {message}")
            
    # Log the input parameters
    debug_print(f"Input parameters - State: {state}, District: {district}, Market: {market}, Commodity: {commodity}")
            
    # Create headless or non-headless browser based on debug setting
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if not debug:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
            
    initial_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    debug_print(f"Opening URL: {initial_url}")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(initial_url)
        take_debug_screenshot("initial_page")
        debug_print("Page loaded successfully")

        # Select Price/Arrivals
        try:
            debug_print("Selecting Price/Arrivals dropdown")
            dropdown = Select(driver.find_element("id", 'ddlArrivalPrice'))
            # Log available options for debugging
            options = [o.text for o in dropdown.options]
            debug_print(f"Available Price/Arrivals options: {options}")
            
            dropdown.select_by_visible_text(price_arrival)
            debug_print(f"Selected '{price_arrival}' from Price/Arrivals dropdown")
            time.sleep(2)
            take_debug_screenshot("after_price_arrival_selection")
        except Exception as e:
            debug_print(f"Error selecting Price/Arrivals: {e}")
            take_debug_screenshot("error_price_arrival")
            driver.quit()
            raise ValueError(f"Price/Arrivals option '{price_arrival}' not found in dropdown.")

        # Select commodity
        try:
            debug_print("Selecting Commodity dropdown")
            dropdown = Select(driver.find_element("id", 'ddlCommodity'))
            # Log available options for debugging
            options = [o.text for o in dropdown.options]
            debug_print(f"Available Commodity options (first 5): {options[:5]}...")
            debug_print(f"Total Commodity options: {len(options)}")
            debug_print(f"Trying to select commodity: '{commodity}'")
            
            dropdown.select_by_visible_text(commodity)
            debug_print(f"Selected '{commodity}' from Commodity dropdown")
            time.sleep(2)
            take_debug_screenshot("after_commodity_selection")
        except Exception as e:
            debug_print(f"Error selecting Commodity: {e}")
            take_debug_screenshot("error_commodity")
            driver.quit()
            raise ValueError(f"Commodity '{commodity}' not found in dropdown: {str(e)}")

        # Select state
        try:
            debug_print("Selecting State dropdown")
            dropdown = Select(driver.find_element("id", 'ddlState'))
            # Log available options for debugging
            options = [o.text for o in dropdown.options]
            debug_print(f"Available State options: {options}")
            debug_print(f"Trying to select state: '{state}'")
            
            dropdown.select_by_visible_text(state)
            debug_print(f"Selected '{state}' from State dropdown")
            time.sleep(2)
            take_debug_screenshot("after_state_selection")
        except Exception as e:
            debug_print(f"Error selecting State: {e}")
            take_debug_screenshot("error_state")
            driver.quit()
            raise ValueError(f"State '{state}' not found in dropdown: {str(e)}")

        # Wait for district dropdown to update and contain the desired district
        def district_option_present(driver):
            try:
                district_dropdown = Select(driver.find_element("id", 'ddlDistrict'))
                options = [option.text.strip() for option in district_dropdown.options]
                debug_print(f"Current district options: {options}")
                return any(option.text.strip() == district for option in district_dropdown.options)
            except:
                debug_print("Error checking district options")
                return False

        try:
            debug_print(f"Waiting for district '{district}' to appear in dropdown")
            WebDriverWait(driver, 10).until(district_option_present)
            dropdown = Select(driver.find_element("id", 'ddlDistrict'))
            
            # Log available options for debugging
            options = [o.text for o in dropdown.options]
            debug_print(f"Available District options: {options}")
            debug_print(f"Trying to select district: '{district}'")
            
            dropdown.select_by_visible_text(district)
            debug_print(f"Selected '{district}' from District dropdown")
            time.sleep(2)
            take_debug_screenshot("after_district_selection")
        except Exception as e:
            debug_print(f"Error selecting District: {e}")
            take_debug_screenshot("error_district")
            driver.quit()
            raise ValueError(f"District '{district}' not found in dropdown after waiting: {str(e)}")

        # Select market
        try:
            debug_print("Selecting Market dropdown")
            dropdown = Select(driver.find_element("id", 'ddlMarket'))
            
            # Log available options for debugging
            options = [o.text for o in dropdown.options]
            debug_print(f"Available Market options (first 5): {options[:5]}...")
            debug_print(f"Total Market options: {len(options)}")
            debug_print(f"Trying to select market: '{market}'")
            
            # Try exact match first
            try:
                dropdown.select_by_visible_text(market)
                debug_print(f"Selected '{market}' from Market dropdown (exact match)")
            except:
                debug_print("Exact match failed, trying flexible matching")
                # If exact match fails, try a more flexible approach
                market_options = [option.text.strip() for option in dropdown.options]
                
                # Try to find a close match ignoring case
                match_found = False
                for option_text in market_options:
                    if market.lower() == option_text.lower() or market.lower() in option_text.lower():
                        debug_print(f"Found close match: '{option_text}' for '{market}'")
                        dropdown.select_by_visible_text(option_text)
                        match_found = True
                        break
                        
                if not match_found:
                    debug_print(f"No match found for market '{market}' in options")
                    raise ValueError(f"No close match for market '{market}' found")
                    
            time.sleep(2)
            take_debug_screenshot("after_market_selection")
        except Exception as e:
            debug_print(f"Error selecting Market: {e}")
            take_debug_screenshot("error_market")
            driver.quit()
            raise ValueError(f"Market '{market}' not found in dropdown. Error: {str(e)}")

        # Set Date From and Date To
        today = datetime.now()
        default_from = (today - timedelta(days=7)).strftime('%d-%b-%Y')
        default_to = today.strftime('%d-%b-%Y')
        date_from_val = date_from if date_from else default_from
        date_to_val = date_to if date_to else default_to
        
        debug_print(f"Setting date range: From '{date_from_val}' To '{date_to_val}'")
        
        try:
            date_input_from = driver.find_element(By.ID, "txtDate")
            date_input_from.clear()
            date_input_from.send_keys(date_from_val)
            debug_print("Set From date")
            time.sleep(2)
            
            date_input_to = driver.find_element(By.ID, "txtDateTo")
            date_input_to.clear()
            date_input_to.send_keys(date_to_val)
            debug_print("Set To date")
            time.sleep(2)
            
            take_debug_screenshot("after_date_selection")
        except Exception as e:
            debug_print(f"Error setting dates: {e}")
            take_debug_screenshot("error_date")
            driver.quit()
            raise RuntimeError(f"Date input fields not found. Error: {str(e)}")

        # Click Go
        try:
            debug_print("Clicking Go button")
            button = driver.find_element("id", 'btnGo')
            button.click()
            debug_print("Go button clicked")
            time.sleep(2)
            take_debug_screenshot("after_button_click")
        except Exception as e:
            debug_print(f"Error clicking Go button: {e}")
            take_debug_screenshot("error_button")
            driver.quit()
            raise RuntimeError(f"Go button not found. Error: {str(e)}")

        driver.implicitly_wait(10)

        # Wait for the table to be present (increased timeout)
        debug_print("Waiting for data table to appear...")
        try:
            # First try to find the 'Both Price and Arrival' table
            table = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'cphBody_GridViewBoth'))
            )
            table_id = 'cphBody_GridViewBoth'
            debug_print("Found 'Both Price and Arrival' table")
        except Exception as e1:
            debug_print(f"Error finding 'Both' table: {e1}")
            try:
                # Try to find the price data table
                table = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'cphBody_GridPriceData'))
                )
                table_id = 'cphBody_GridPriceData'
                debug_print("Found price data table")
            except Exception as e2:
                debug_print(f"Error finding price table: {e2}")
                try:
                    # Try to find the arrival data table
                    table = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'cphBody_GridArrivalData'))
                    )
                    table_id = 'cphBody_GridArrivalData'
                    debug_print("Found arrival data table")
                except Exception as e3:
                    debug_print(f"Error finding arrival table: {e3}")
                    debug_print("Checking page for errors or messages")
                    take_debug_screenshot("table_not_found")
                    
                    # Capture any error messages on the page
                    try:
                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')
                        # Look for common error message elements
                        error_msgs = soup.find_all(['div', 'span', 'label'], class_=['error', 'errorMsg', 'alert'])
                        if error_msgs:
                            debug_print(f"Found potential error messages: {[msg.text for msg in error_msgs]}")
                    except Exception as e4:
                        debug_print(f"Error parsing page for messages: {e4}")
                        
                    raise RuntimeError("No data table found on the page")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the specific table by ID
        table = soup.find('table', id=table_id)
        
        if not table:
            raise RuntimeError(f"Table with ID {table_id} not found in the page source")
            
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

        return jsonList
    finally:
        driver.quit()

def scrape_commodity_by_location(
    lat: float,
    lon: float,
    commodity: str,
    price_arrival: str = "Both",
    debug: bool = False
) -> Dict[str, Any]:
    """
    Scrapes commodity price and arrival data from the Agmarknet website using
    latitude and longitude to determine the appropriate state, district, and market.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodity: The commodity name (e.g., "Rice", "Wheat")
        price_arrival: Type of data to fetch - "Price", "Arrival", or "Both" (default)
        debug: If True, enables debug mode with screenshots and logging
        
    Returns:
        Dictionary containing:
        - state: Determined state name
        - district: Determined district name
        - market: Market name used for the query
        - commodity: Commodity name
        - data: List of dictionaries with the scraped commodity data
        - latest_prices: The latest price information
        - error: Error message if any occurred
    
    Example:
        >>> results = scrape_commodity_by_location(
        ...     28.6139, 77.2090,  # Delhi coordinates
        ...     "Rice"
        ... )
    """
    result = {
        "state": None,
        "district": None,
        "market": None,
        "commodity": commodity,
        "data": [],
        "latest_prices": {},
        "error": None
    }
    
    try:
        # Step 1: Try to get the nearest location from our database first
        # This uses direct coordinate-based lookup for better accuracy
        from .geo_utils import get_nearest_location_from_database
        nearest_location = get_nearest_location_from_database(lat, lon)
        
        if nearest_location:
            state = nearest_location["state"]
            district = nearest_location["district"]
        else:
            # Fall back to traditional reverse geocoding
            state, district = get_state_district(lat, lon)
        
        result["state"] = state
        result["district"] = district
        
        # If district is not found, use the state capital or a major city
        if not district:
            district = state  # In many cases, the state and its capital city share the same name
        
        # Step 2: Get potential markets for the district, prioritized by distance
        markets = find_markets_by_coordinates(lat, lon, commodity)
        result["markets_found"] = markets
        
        # Step 3: Try to get data for each market until we find one with results
        successful_market = None
        market_data = []
        
        # Set date range (2 weeks ago to today)
        today = datetime.now()
        two_weeks_ago = today - timedelta(days=14)
        date_from = two_weeks_ago.strftime('%d-%b-%Y')
        date_to = today.strftime('%d-%b-%Y')
        
        for market in markets:
            try:
                market_data = scrape_commodity(
                    state=state,
                    district=district,
                    market=market,
                    commodity=commodity,
                    price_arrival=price_arrival,
                    date_from=date_from,
                    date_to=date_to
                )
                
                if market_data and len(market_data) > 0:
                    successful_market = market
                    break
            except Exception:
                continue
        
        # Step 4: Process the results
        if successful_market:
            result["market"] = successful_market
            result["data"] = market_data
            result["latest_prices"] = get_latest_prices(market_data)
        else:
            result["error"] = f"No data found for {commodity} in any market in {district}, {state}"
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def get_all_commodity_prices(lat: float, lon: float, commodities: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Gets price data for multiple commodities based on location.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        commodities: List of commodity names
        
    Returns:
        Dictionary mapping each commodity to its price data
    """
    result = {}
    
    # If no commodities specified, try to get common crops for the region
    if not commodities:
        commodities = get_common_crops(lat, lon)
    
    # Process each commodity
    for commodity in commodities:
        try:
            commodity_data = scrape_commodity_by_location(lat, lon, commodity)
            result[commodity] = commodity_data
        except Exception as e:
            result[commodity] = {"error": str(e)}
    
    return result

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
    # Filter by variety if specified
    filtered_data = data
    if commodity_variety:
        filtered_data = [item for item in data if item.get('Variety') == commodity_variety]
    
    if not filtered_data:
        return {}
    
    # Sort by date (most recent first)
    sorted_data = sorted(
        filtered_data, 
        key=lambda x: datetime.strptime(x.get('Reported Date', '01 Jan 2000'), '%d %b %Y'),
        reverse=True
    )
    
    latest = sorted_data[0]
    
    # Return formatted result
    return {
        'variety': latest.get('Variety', 'Unknown'),
        'min_price': float(latest.get('Min Price', '0')),
        'max_price': float(latest.get('Max Price', '0')),
        'modal_price': float(latest.get('Modal Price', '0')),
        'date': latest.get('Reported Date', 'Unknown'),
        'market': latest.get('Market Name', 'Unknown')
    }

if __name__ == "__main__":
    print("Farmora Commodity Price Tool")
    print("---------------------------\n")
    print("1. Search by state/district/market")
    print("2. Search by coordinates (latitude/longitude)")
    choice = input("\nEnter your choice (1/2): ")
    
    try:
        if choice == "1":
            # Traditional search by state/district/market
            state = input("Enter state: ")
            commodity = input("Enter commodity: ")
            district = input("Enter district: ")
            market = input("Enter market: ")
            price_arrival = input("Enter Price/Arrivals (Price, Arrival, Both) [default: Both]: ") or "Both"
            date_from = input("Enter Date From (dd-MMM-yyyy) [default: 2 weeks ago]: ")
            date_to = input("Enter Date To (dd-MMM-yyyy) [default: today]: ")

            results = scrape_commodity(
                state,
                commodity,
                district,
                market,
                price_arrival,
                date_from,
                date_to
            )
            
            print(f"Found {len(results)} records\n")
            
            # Get all varieties in the results
            varieties = set(item.get('Variety', 'Unknown') for item in results)
            print(f"Available varieties: {', '.join(varieties)}\n")
            
            # Show most recent price for each variety
            print("Latest prices by variety:")
            for variety in varieties:
                latest = get_latest_prices(results, variety)
                if latest:
                    print(f"  {variety}: ₹{latest['modal_price']} (₹{latest['min_price']} - ₹{latest['max_price']}) on {latest['date']}")
            
        elif choice == "2":
            # Search by coordinates
            try:
                lat = float(input("Enter latitude (e.g., 28.6139 for Delhi): "))
                lon = float(input("Enter longitude (e.g., 77.2090 for Delhi): "))
                
                # Get the state and district
                state, district = get_state_district(lat, lon)
                print(f"\nDetected location: {district}, {state}")
                
                # Ask for commodities
                commodity_input = input("Enter commodities (comma-separated, e.g., Rice,Wheat) [press Enter for suggestions]: ")
                
                if commodity_input.strip():
                    commodities = [c.strip() for c in commodity_input.split(",")]
                else:
                    # Get common crops for the region
                    commodities = get_common_crops(lat, lon)
                    print(f"Using common crops for the region: {', '.join(commodities)}")
                
                # Get price data for all specified commodities
                all_results = get_all_commodity_prices(lat, lon, commodities)
                
                # Print the results
                for commodity, result in all_results.items():
                    print(f"\n=== {commodity} ===")
                    
                    if "error" in result and result["error"]:
                        print(f"Error: {result['error']}")
                        continue
                    
                    print(f"Location: {result.get('district', 'Unknown')}, {result.get('state', 'Unknown')}")
                    print(f"Market: {result.get('market', 'Unknown')}")
                    
                    latest = result.get('latest_prices', {})
                    if latest:
                        print(f"Latest price: ₹{latest.get('modal_price', 'N/A')} (₹{latest.get('min_price', 'N/A')} - ₹{latest.get('max_price', 'N/A')})")
                        print(f"Variety: {latest.get('variety', 'Unknown')}")
                        print(f"Date: {latest.get('date', 'Unknown')}")
                    
                    records = result.get('data', [])
                    print(f"Total records: {len(records)}")
            
            except ValueError:
                print("Error: Coordinates must be valid floating-point numbers")
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you entered the correct state, district, and market names")
        print("2. Check that the website is accessible") 
        print("3. For coordinates, ensure they are valid numbers for India")