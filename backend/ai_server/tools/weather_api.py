import requests
from typing import Dict

def get_weather(lat: float, lon: float) -> Dict:
	"""
	Fetches current weather data from Open-Meteo API for the given latitude and longitude.
	Args:
		lat (float): Latitude
		lon (float): Longitude
	Returns:
		Dict: Weather data as returned by the API
	Raises:
		Exception: If the API call fails or returns an error
	"""
	url = (
		f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
		"&current_weather=true"
	)
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f"Open-Meteo API error: {response.status_code} {response.text}")
	data = response.json()
	if 'current_weather' not in data:
		raise Exception(f"No current weather data found in response: {data}")
	return data['current_weather']

if __name__ == "__main__":
	lat, lon = float(input("Enter latitude: ")), float(input("Enter longitude: "))
	weather = get_weather(lat, lon)
	print("Current weather:")
	for key, value in weather.items():
		print(f"  {key}: {value}")
