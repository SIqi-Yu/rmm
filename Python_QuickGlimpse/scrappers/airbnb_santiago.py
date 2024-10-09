import gzip
import shutil
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import matplotlib.pyplot as plt
import json
import numpy as np


CHROME_DRIVER_PATH = '/opt/homebrew/bin/chromedriver'

def normalize_city_name(city_name):
    return re.sub(r'\W+', '', city_name.lower())

def click_listings_csv(city_name):
    chrome_options = Options()
    
    prefs = {
        "profile.managed_default_content_settings.images": 2, 
        "profile.managed_default_content_settings.stylesheets": 2,
        "download.default_directory": download_dir,  
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('http://insideairbnb.com/get-the-data.html')
    time.sleep(3)
    normalized_city = normalize_city_name(city_name)
    links = driver.find_elements(By.TAG_NAME, 'a')
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)

    for link in links:
        href = link.get_attribute('href')
        if href and 'listings.csv' in href:
            normalized_href = normalize_city_name(href)
            if normalized_city in normalized_href:
                print(f"Found link for {city_name}: {href}")
                actions.move_to_element(link).perform()
                wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'a')))
                link.click()
                break
    else:
        print(f"No listings.csv file found for {city_name}")

    time.sleep(5)
    driver.quit()

def extract_gz_file(download_dir, destination_dir, city_name):
    for file_name in os.listdir(download_dir):
        if file_name.endswith('.gz'):
            gz_file_path = os.path.join(download_dir, file_name)
            print(f"Found GZ file: {gz_file_path}")
            
            # Append city name to the front of the extracted file name
            output_file_name = f'{city_name}_listings.csv'
            output_file_path = os.path.join(destination_dir, output_file_name)
            
            try:
                # Extract the file
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(output_file_path, 'wb') as out_file:
                        shutil.copyfileobj(gz_file, out_file)
                print(f"Extracted GZ file to: {output_file_path}")
                
                # Delete the original gz file
                os.remove(gz_file_path)
                print(f"Deleted the GZ file: {gz_file_path}")
                
                return output_file_path
            except PermissionError as e:
                print(f"Permission error during extraction or deletion: {e}")
                return None
            except OSError as e:
                print(f"Error during file operation: {e}")
                return None
    else:
        print("No GZ file found.")
        return None
def load_and_filter_csv(file_path, city_name):
    try:
        df = pd.read_csv(file_path)
        columns_to_keep = ['review_scores_rating', 'price', 'bedrooms', 'reviews_per_month']
        df_filtered = df[columns_to_keep]
        df_filtered['price'] = df_filtered['price'].replace({'\$': '', ',': ''}, regex=True).astype(float)

        # Data processing
        df_filtered = remove_outliers(df_filtered, 'price')
        stats_dict = calculate_average_price_per_bedroom(df_filtered)
        
        # Save stats_dict to json
        filename = f"offline/{city_name}_bedroom_stats.json"
        # Save as JSON file
        with open(filename, 'w') as json_file:
            json.dump(stats_dict, json_file, indent=4)

        print(f"Saved bedroom statistics to {filename}")

        # Save the filtered data to a new CSV file
        output_file_name = f'cleaned_{file_path.split("/")[1].split("_")[0].lower().replace(" ", "_")}.csv'
        output_path = os.path.join(os.path.dirname(file_path), output_file_name)
        df_filtered.to_csv(output_path, index=False)
        print(f"Cleaned data saved to: {output_path}")

        return stats_dict
    except Exception as e:
        print(f"Error loading or filtering CSV: {e}")
        return None

def remove_outliers(df, column_name:str, Q1=0.25, Q3=0.75):
    q1 = df[column_name].quantile(Q1)
    q3 = df[column_name].quantile(Q3)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    df = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]
    return df

def calculate_average_price_per_bedroom(df):
    """
    Calculates statistics for each bedroom type:
    1) For listings with >3 star ratings: average price, min price, max price, and count
    2) For all listings: average price, min price, max price, and count
    """
    # Filter the DataFrame to include only entries with a 'review_scores_rating' above 3 stars
    df_filtered = df[df['review_scores_rating'] > 3]

    # Calculate stats for listings with >3 star ratings
    stats_above_3 = df_filtered.groupby('bedrooms')['price'].agg(['mean', 'min', 'max', 'count']).rename(columns={'mean': 'average_price'})

    # Calculate stats for all listings
    stats_all = df.groupby('bedrooms')['price'].agg(['mean', 'min', 'max', 'count']).rename(columns={'mean': 'average_price'})

    stats_above_3_dict = stats_above_3.to_dict(orient='index')
    stats_all_dict = stats_all.to_dict(orient='index')

    combined_stats = {
        'above_3_stars': stats_above_3_dict,
        'all_listings': stats_all_dict
    }
    return combined_stats

def get_user_city():
    city = input("Enter an additional city name (e.g., 'Seattle, WA'): ")
    return city

def get_city_data(city_name):
    filepath = "offline/" + city_name + "_listings.csv"
    return load_and_filter_csv(filepath, city_name)

def plot_average_prices(data):
    # Get all unique bedroom keys from both datasets
    bedrooms = sorted(set(data['above_3_stars'].keys()).union(data['all_listings'].keys()))
    
    avg_prices_above_3 = [data['above_3_stars'].get(bedroom, {}).get('average_price', None) for bedroom in bedrooms]
    avg_prices_all = [data['all_listings'].get(bedroom, {}).get('average_price', None) for bedroom in bedrooms]

    plt.figure(figsize=(10,6))
    plt.plot(bedrooms, avg_prices_above_3, label='>3 Stars', marker='o')
    plt.plot(bedrooms, avg_prices_all, label='All Listings', marker='o')
    plt.title('Average Price by Bedroom Type')
    plt.xlabel('Number of Bedrooms')
    plt.ylabel('Average Price ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig('offline/City_average_prices.png')


def plot_price_ranges(data):
    # Get all unique bedroom keys from both datasets
    bedrooms = sorted(set(data['above_3_stars'].keys()).union(data['all_listings'].keys()))
    
    # Use .get() with default values to handle missing data
    min_prices_above_3 = [data['above_3_stars'].get(bedroom, {}).get('min', np.nan) for bedroom in bedrooms]
    max_prices_above_3 = [data['above_3_stars'].get(bedroom, {}).get('max', np.nan) for bedroom in bedrooms]
    
    min_prices_all = [data['all_listings'].get(bedroom, {}).get('min', np.nan) for bedroom in bedrooms]
    max_prices_all = [data['all_listings'].get(bedroom, {}).get('max', np.nan) for bedroom in bedrooms]

    plt.figure(figsize=(10,6))
    
    # Plot min-max range for >3 stars
    plt.fill_between(bedrooms, min_prices_above_3, max_prices_above_3,
                     color='blue', alpha=0.1, label='>3 Stars')
    
    # Plot min-max range for all listings
    plt.fill_between(bedrooms, min_prices_all, max_prices_all,
                     color='orange', alpha=0.1, label='All Listings')
    
    plt.title('Min and Max Prices by Bedroom Type')
    plt.xlabel('Number of Bedrooms')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)
    
    plt.savefig('offline/City_price_ranges.png')


download_dir = os.path.join(os.getcwd(), 'downloads')
destination_dir = os.path.join(os.getcwd(), 'offline')

def main(city:str="Dallas", use_offline:bool = False):
    try:
        if not use_offline:
            # Downloads data
            click_listings_csv(city)
            # Extracts csv
            extract_gz_file(download_dir, destination_dir, city)
        stats_dict = get_city_data(city)
        plot_average_prices(stats_dict)
        plot_price_ranges(stats_dict)
        return stats_dict
    except Exception as e:
        return None
if __name__ == "__main__":
    main()
