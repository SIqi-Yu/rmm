from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from difflib import get_close_matches
import json

CHROME_DRIVER_PATH = '/opt/homebrew/bin/chromedriver'

def get_attraction_data(keyword, location:str="Pittsburgh"):
    location = location.lower()
    # Maps the location to the website URL for that city
    cities_map = {
        "pittsburgh": "Pittsburgh_PA",
        "dallas": "Dallas_TX",
        "new york": "New_York_NY",
        "los angeles": "Los_Angeles_CA",
        "chicago": "Chicago_IL",
        "houston": "Houston_TX",
        "phoenix": "Phoenix_AZ",
        "philadelphia": "Philadelphia_PA",
        "san antonio": "San_Antonio_TX",
        "san diego": "San_Diego_CA",
    }
    chrome_options = Options()
    chrome_options.add_argument("--headless÷")  # Run in headless mode if needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Please edit this
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(f"https://travel.usnews.com/{cities_map[location]}/Things_To_Do/")

    titles = driver.find_elements(By.CSS_SELECTOR, "div.Raw-slyvem-0.icSGnd")
    addresses = driver.find_elements(By.CSS_SELECTOR, "span.DetailCardTour__StyledAddress-sc-1f2q998-9 span")
    time_to_spend = driver.find_elements(By.XPATH, "//div[text()='TIME TO SPEND']/preceding-sibling::div")
    types = driver.find_elements(By.XPATH, "//div[text()='TYPE']/preceding-sibling::div")

    titles_text = [title.text for title in titles]
    time_to_spend_text = [time.text for time in time_to_spend]
    types_text = [type_.text for type_ in types]
    
    titles = [title for title in titles_text if title.strip() != '']
    time_to_spend = [time for time in time_to_spend_text if time.strip() != '']
    types = [type_ for type_ in types_text if type_.strip() != '']

    attractions = []
    for i in range(13):
        item = {
            "title": titles[i],
            "time_to_spend": time_to_spend[i],
            "type": types[i]
        }
        attractions.append(item)

    driver.quit()
    # Save attractions to a JSON file
    filename = f"offline/{location.replace(' ', '_').lower()}_attractions.json"
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(attractions, json_file, ensure_ascii=False, indent=4)

    return attractions

def get_attraction_data_offline(keyword, location:str="Pittsburgh"):
    filename = f"offline/{location.replace(' ', '_').lower()}_attractions.json"
    print(f"Offline data being used for: {location}")
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            attractions = json.load(json_file)
        print(f"Attraction data loaded from {filename}")
        return attractions
    except FileNotFoundError:
        print(f"No attraction data found for {location}")
        return None
    
def main(keyword:str="Museums", location="Pittsburgh", use_offline:bool = False):
    try:
        if not use_offline:
            return get_attraction_data(keyword, location)
        else:
            return get_attraction_data_offline(keyword, location)
    except Exception as e:
        return None
if __name__ == "__main__":
    user_input = input("Enter a type of attraction (e.g., 'Museums', 'Parks', 'Shopping'): ")
    main(user_input)
