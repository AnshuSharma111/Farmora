"""
Enhanced database of districts with geolocation information.

This file creates a JSON database of Indian districts with 
their corresponding geographical coordinates to improve 
the accuracy of location-based commodity price lookup.
"""

import json
import os
from pathlib import Path

# Define districts with their respective states and coordinates
districts_data = [
    # Punjab
    {"state": "Punjab", "district": "Ludhiana", "latitude": 30.9010, "longitude": 75.8573},
    {"state": "Punjab", "district": "Amritsar", "latitude": 31.6340, "longitude": 74.8723},
    {"state": "Punjab", "district": "Patiala", "latitude": 30.3398, "longitude": 76.3869},
    {"state": "Punjab", "district": "Jalandhar", "latitude": 31.3260, "longitude": 75.5762},
    {"state": "Punjab", "district": "Bathinda", "latitude": 30.2110, "longitude": 74.9455},
    {"state": "Punjab", "district": "Hoshiarpur", "latitude": 31.5143, "longitude": 75.9115},
    {"state": "Punjab", "district": "Gurdaspur", "latitude": 32.0419, "longitude": 75.4053},
    {"state": "Punjab", "district": "Moga", "latitude": 30.8230, "longitude": 75.1712},
    {"state": "Punjab", "district": "Ferozepur", "latitude": 30.9331, "longitude": 74.6225},
    {"state": "Punjab", "district": "Sangrur", "latitude": 30.2457, "longitude": 75.8454},
    
    # Haryana
    {"state": "Haryana", "district": "Karnal", "latitude": 29.6857, "longitude": 76.9905},
    {"state": "Haryana", "district": "Ambala", "latitude": 30.3752, "longitude": 76.7821},
    {"state": "Haryana", "district": "Hisar", "latitude": 29.1492, "longitude": 75.7217},
    {"state": "Haryana", "district": "Gurugram", "latitude": 28.4595, "longitude": 77.0266},
    {"state": "Haryana", "district": "Kurukshetra", "latitude": 29.9695, "longitude": 76.8783},
    {"state": "Haryana", "district": "Panipat", "latitude": 29.3909, "longitude": 76.9635},
    {"state": "Haryana", "district": "Rohtak", "latitude": 28.8955, "longitude": 76.6066},
    {"state": "Haryana", "district": "Sonipat", "latitude": 28.9931, "longitude": 77.0151},
    {"state": "Haryana", "district": "Faridabad", "latitude": 28.4089, "longitude": 77.3178},
    {"state": "Haryana", "district": "Bhiwani", "latitude": 28.7929, "longitude": 76.1397},
    
    # Himachal Pradesh
    {"state": "Himachal Pradesh", "district": "Shimla", "latitude": 31.1048, "longitude": 77.1734},
    {"state": "Himachal Pradesh", "district": "Solan", "latitude": 30.9045, "longitude": 77.0968},
    {"state": "Himachal Pradesh", "district": "Kangra", "latitude": 32.0999, "longitude": 76.2691},
    {"state": "Himachal Pradesh", "district": "Kullu", "latitude": 31.9592, "longitude": 77.1089},
    {"state": "Himachal Pradesh", "district": "Mandi", "latitude": 31.5892, "longitude": 76.9182},
    {"state": "Himachal Pradesh", "district": "Hamirpur", "latitude": 31.6861, "longitude": 76.5269},
    {"state": "Himachal Pradesh", "district": "Bilaspur", "latitude": 31.3348, "longitude": 76.6870},
    {"state": "Himachal Pradesh", "district": "Sirmaur", "latitude": 30.5678, "longitude": 77.2940},
    {"state": "Himachal Pradesh", "district": "Una", "latitude": 31.4685, "longitude": 76.2708},
    {"state": "Himachal Pradesh", "district": "Chamba", "latitude": 32.5533, "longitude": 76.1258},
    
    # Uttar Pradesh
    {"state": "Uttar Pradesh", "district": "Lucknow", "latitude": 26.8467, "longitude": 80.9462},
    {"state": "Uttar Pradesh", "district": "Kanpur", "latitude": 26.4499, "longitude": 80.3319},
    {"state": "Uttar Pradesh", "district": "Varanasi", "latitude": 25.3176, "longitude": 82.9739},
    {"state": "Uttar Pradesh", "district": "Agra", "latitude": 27.1767, "longitude": 78.0081},
    {"state": "Uttar Pradesh", "district": "Meerut", "latitude": 28.9845, "longitude": 77.7064},
    {"state": "Uttar Pradesh", "district": "Ghaziabad", "latitude": 28.6692, "longitude": 77.4538},
    {"state": "Uttar Pradesh", "district": "Bareilly", "latitude": 28.3670, "longitude": 79.4304},
    {"state": "Uttar Pradesh", "district": "Aligarh", "latitude": 27.8974, "longitude": 78.0880},
    {"state": "Uttar Pradesh", "district": "Moradabad", "latitude": 28.8386, "longitude": 78.7733},
    {"state": "Uttar Pradesh", "district": "Gorakhpur", "latitude": 26.7606, "longitude": 83.3732},
]

def create_districts_database():
    """
    Create a JSON file with district geolocation data
    """
    # Define paths
    data_dir = Path(__file__).resolve().parent.parent / "data"
    districts_file = data_dir / "districts_database.json"
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Save the districts data to JSON file
    with open(districts_file, 'w') as f:
        json.dump(districts_data, f, indent=2)
    
    print(f"Created districts database with {len(districts_data)} entries")
    print(f"Saved to: {districts_file}")

if __name__ == "__main__":
    create_districts_database()
