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
from typing import List, Dict, Optional, Union

def scrape_commodity(
    state: str,
    commodity: str,
    district: str,
    market: str,
    price_arrival: str = "Both",  # "Price", "Arrival", or "Both"
    date_from: str = None,         # e.g., "27-Jul-2025"
    date_to: str = None           # e.g., "18-Aug-2025"
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
    initial_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    driver = webdriver.Chrome()
    try:
        driver.get(initial_url)

        # Select Price/Arrivals
        try:
            dropdown = Select(driver.find_element("id", 'ddlArrivalPrice'))
            dropdown.select_by_visible_text(price_arrival)
            time.sleep(2)
        except Exception:
            driver.quit()
            raise ValueError(f"Price/Arrivals option '{price_arrival}' not found in dropdown.")

        # Select commodity
        try:
            dropdown = Select(driver.find_element("id", 'ddlCommodity'))
            dropdown.select_by_visible_text(commodity)
            time.sleep(2)
        except Exception:
            driver.quit()
            raise ValueError(f"Commodity '{commodity}' not found in dropdown.")

        # Select state
        try:
            dropdown = Select(driver.find_element("id", 'ddlState'))
            dropdown.select_by_visible_text(state)
            time.sleep(2)
        except Exception:
            driver.quit()
            raise ValueError(f"State '{state}' not found in dropdown.")

        # Wait for district dropdown to update and contain the desired district
        def district_option_present(driver):
            district_dropdown = Select(driver.find_element("id", 'ddlDistrict'))
            return any(option.text.strip() == district for option in district_dropdown.options)

        try:
            WebDriverWait(driver, 10).until(district_option_present)
            dropdown = Select(driver.find_element("id", 'ddlDistrict'))
            dropdown.select_by_visible_text(district)
            time.sleep(2)
        except Exception:
            driver.quit()
            raise ValueError(f"District '{district}' not found in dropdown after waiting.")

        # Select market
        try:
            dropdown = Select(driver.find_element("id", 'ddlMarket'))
            
            # Try exact match first
            try:
                dropdown.select_by_visible_text(market)
            except:
                # If exact match fails, try a more flexible approach
                market_options = [option.text.strip() for option in dropdown.options]
                print(f"[DEBUG] Available markets: {market_options[:10]}...")  # Print first 10 for debugging
                
                # Try to find a close match ignoring case
                match_found = False
                for option_text in market_options:
                    if market.lower() == option_text.lower() or market.lower() in option_text.lower():
                        print(f"[DEBUG] Found close match: '{option_text}' for '{market}'")
                        dropdown.select_by_visible_text(option_text)
                        match_found = True
                        break
                        
                if not match_found:
                    raise ValueError(f"No close match for market '{market}' found")
                    
            time.sleep(2)
        except Exception as e:
            driver.quit()
            raise ValueError(f"Market '{market}' not found in dropdown. Error: {str(e)}")

        # Set Date From and Date To
        today = datetime.now()
        default_from = (today - timedelta(days=7)).strftime('%d-%b-%Y')
        default_to = today.strftime('%d-%b-%Y')
        date_from_val = date_from if date_from else default_from
        date_to_val = date_to if date_to else default_to
        try:
            date_input_from = driver.find_element(By.ID, "txtDate")
            date_input_from.clear()
            date_input_from.send_keys(date_from_val)
            time.sleep(2)
            date_input_to = driver.find_element(By.ID, "txtDateTo")
            date_input_to.clear()
            date_input_to.send_keys(date_to_val)
            time.sleep(2)
        except Exception:
            driver.quit()
            raise RuntimeError("Date input fields not found.")

        # Click Go
        try:
            button = driver.find_element("id", 'btnGo')
            button.click()
            time.sleep(2)
        except Exception:
            driver.quit()
            raise RuntimeError("Go button not found.")

        driver.implicitly_wait(10)

        # DEBUG: Save screenshot before waiting for table
        debug_screenshot = f"debug_{int(time.time())}.png"
        driver.save_screenshot(debug_screenshot)
        print(f"[DEBUG] Screenshot saved to {debug_screenshot}")

        # Wait for the table to be present (increased timeout)
        print("[DEBUG] Waiting for results table to appear...")
        try:
            # First try to find the 'Both Price and Arrival' table
            table = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'cphBody_GridViewBoth'))
            )
            table_id = 'cphBody_GridViewBoth'
            print("[DEBUG] Found 'Both Price and Arrival' table")
        except:
            try:
                # Try to find the price data table
                table = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'cphBody_GridPriceData'))
                )
                table_id = 'cphBody_GridPriceData'
                print("[DEBUG] Found price data table")
            except:
                try:
                    # Try to find the arrival data table
                    table = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'cphBody_GridArrivalData'))
                    )
                    table_id = 'cphBody_GridArrivalData'
                    print("[DEBUG] Found arrival data table")
                except:
                    print("[ERROR] Could not find any data table")
                    raise RuntimeError("No data table found on the page")
                
        print(f"[DEBUG] Table found with ID: {table_id}")
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
            
        print(f"[DEBUG] Headers found: {headers}")
            
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
    state = input("Enter state: ")
    commodity = input("Enter commodity: ")
    district = input("Enter district: ")
    market = input("Enter market: ")
    price_arrival = input("Enter Price/Arrivals (Price, Arrival, Both): ")
    date_from = input("Enter Date From (dd-MMM-yyyy): ")
    date_to = input("Enter Date To (dd-MMM-yyyy): ")

    try:
        print(f"\nScraping data for {commodity} from {market}...\n")
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
        
        print("\nComplete data:")
        for item in results:
            print(item)

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you entered the correct state, district, and market names")
        print("2. Check that the website is accessible")
        print("3. Ensure the correct date format (dd-MMM-yyyy)")