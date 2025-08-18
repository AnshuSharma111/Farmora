"""
Enhanced Markets database with location information.

This file creates a JSON database of Indian agricultural markets with 
their corresponding districts to improve the accuracy of location-based
commodity price lookup.
"""

import json
import os
from pathlib import Path

# Define markets with their respective districts
markets_data = [
    # Punjab
    {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana"},
    {"state": "Punjab", "district": "Ludhiana", "market": "Khanna"},
    {"state": "Punjab", "district": "Ludhiana", "market": "Jagraon"},
    {"state": "Punjab", "district": "Ludhiana", "market": "Samrala"},
    {"state": "Punjab", "district": "Amritsar", "market": "Amritsar"},
    {"state": "Punjab", "district": "Patiala", "market": "Patiala"},
    {"state": "Punjab", "district": "Jalandhar", "market": "Jalandhar"},
    {"state": "Punjab", "district": "Bathinda", "market": "Bathinda"},
    
    # Haryana
    {"state": "Haryana", "district": "Karnal", "market": "Karnal"},
    {"state": "Haryana", "district": "Ambala", "market": "Ambala"},
    {"state": "Haryana", "district": "Hisar", "market": "Hisar"},
    {"state": "Haryana", "district": "Gurugram", "market": "Gurugram"},
    {"state": "Haryana", "district": "Kurukshetra", "market": "Kurukshetra"},
    
    # Himachal Pradesh
    {"state": "Himachal Pradesh", "district": "Shimla", "market": "Shimla"},
    {"state": "Himachal Pradesh", "district": "Shimla", "market": "Theog"},
    {"state": "Himachal Pradesh", "district": "Shimla", "market": "Rohru"},
    {"state": "Himachal Pradesh", "district": "Solan", "market": "Solan"},
    {"state": "Himachal Pradesh", "district": "Solan", "market": "Parwanoo"},
    {"state": "Himachal Pradesh", "district": "Solan", "market": "Waknaghat"},
    {"state": "Himachal Pradesh", "district": "Solan", "market": "Arki"},
    {"state": "Himachal Pradesh", "district": "Solan", "market": "Dharampur"},
    {"state": "Himachal Pradesh", "district": "Kangra", "market": "Dharamshala"},
    {"state": "Himachal Pradesh", "district": "Kangra", "market": "Palampur"},
    {"state": "Himachal Pradesh", "district": "Kullu", "market": "Kullu"},
    {"state": "Himachal Pradesh", "district": "Mandi", "market": "Mandi"},
    
    # Uttar Pradesh
    {"state": "Uttar Pradesh", "district": "Lucknow", "market": "Lucknow"},
    {"state": "Uttar Pradesh", "district": "Kanpur", "market": "Kanpur"},
    {"state": "Uttar Pradesh", "district": "Varanasi", "market": "Varanasi"},
    {"state": "Uttar Pradesh", "district": "Agra", "market": "Agra"},
    {"state": "Uttar Pradesh", "district": "Meerut", "market": "Meerut"},
]

def create_markets_database():
    """
    Create a JSON file with markets data
    """
    # Define paths
    data_dir = Path(__file__).resolve().parent.parent / "data"
    markets_file = data_dir / "markets_database.json"
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Save the markets data to JSON file
    with open(markets_file, 'w') as f:
        json.dump(markets_data, f, indent=2)
    
    print(f"Created markets database with {len(markets_data)} entries")
    print(f"Saved to: {markets_file}")

if __name__ == "__main__":
    create_markets_database()
