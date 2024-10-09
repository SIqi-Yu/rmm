import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import json
import os

def get_weather_data_online(lat, lon, city_name):
    # Print the city name being processed
    url = f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for {city_name} at coordinates: {lat}, {lon}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract weather data
    weather_data = {}
    weather_data['location'] = city_name
    
    # Extracting the extended forecast
    forecast_items = soup.find_all("div", class_="tombstone-container")
    for item in forecast_items:
        day = item.find("p", class_="period-name").text  # Day of the week
        temp_high = item.find("p", class_="temp temp-high").text if item.find("p", class_="temp temp-high") else "N/A"
        temp_low = item.find("p", class_="temp temp-low").text if item.find("p", class_="temp temp-low") else "N/A"
        description = item.find("p", class_="short-desc").text  # Weather description

        weather_data[day] = {
            'high': temp_high,
            'low': temp_low,
            'description': description
        }

    # Corrected ID for detailed forecast
    detailed_forecast = soup.find('div', id='detailed-forecast')
    if detailed_forecast:
        detailed_items = detailed_forecast.find_all("div", class_="row row-odd row-forecast") + \
                        detailed_forecast.find_all("div", class_="row row-even row-forecast")
        for item in detailed_items:
            day_label = item.find("b").text
            detailed_text = item.find("div", class_="col-sm-10 forecast-text").text.strip()

            # Update the existing entry with detailed information
            if day_label in weather_data:
                weather_data[day_label]['detailed'] = detailed_text
            else:
                weather_data[day_label] = {'detailed': detailed_text}
    
    # Saves file offline
    json_filename = f"offline/{city_name.replace(' ', '_')}_weather.json"
    with open(json_filename, 'w', encoding='utf-8') as file:
        json.dump(weather_data, file, ensure_ascii=False, indent=4)

    return weather_data

def get_weather_data_offline(city_name:str):
    print(f"Offline data being used for: {city_name}")
    json_filename = f"offline/{city_name.replace(' ', '_')}_weather.json"
    if os.path.exists(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as file:
            weather_data = json.load(file)
        print(f"Weather data loaded from {json_filename}")
        return weather_data
    else:
        print(f"No offline data found for {city_name}")
        return None

def main(user_input:str=None, use_offline:bool = False):
    try:
        if user_input is None:
            user_input = input("Enter a city name: ")

        cities = [
            {"name": "Pittsburgh, PA", "lat": 40.44, "lon": -79.99},
            {"name": "New York, NY", "lat": 40.71, "lon": -74.01},
            {"name": "Los Angeles, CA", "lat": 34.05, "lon": -118.25},
            {"name": "Chicago, IL", "lat": 41.87, "lon": -87.62},
            {"name": "Houston, TX", "lat": 29.76, "lon": -95.36},
            {"name": "Phoenix, AZ", "lat": 33.45, "lon": -112.07},
            {"name": "Philadelphia, PA", "lat": 39.95, "lon": -75.16},
            {"name": "San Antonio, TX", "lat": 29.42, "lon": -98.49},
            {"name": "San Diego, CA", "lat": 32.71, "lon": -117.16},
            {"name": "Dallas, TX", "lat": 32.78, "lon": -96.80}
        ]

        # Extract city names for matching
        city_names = [city['name'] for city in cities]
        
        # Find the best match for the user input
        best_match, score = process.extractOne(user_input, city_names)  # Corrected method name
        if score < 80:  # Threshold for matching
            raise Exception("City not found") # Exit the program
        # Get the matched city data
        matched_city = next(city for city in cities if city['name'] == best_match)
        # Fetch and display weather data
        if not use_offline:
            data = get_weather_data_online(matched_city['lat'], matched_city['lon'], matched_city['name'])
        else: 
            data = get_weather_data_offline(matched_city['name'])
        return data

    except Exception as e:
        return None

if __name__ == "__main__":
    main()