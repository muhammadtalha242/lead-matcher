import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
import logging
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import shelve
import json
import os

# Ensure nltk stopwords are downloaded
nltk.download('stopwords')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _extract_location_parts(location):
    """Extract and categorize location parts into states and cities."""
    locations = set()
    german_states = {
        'baden-württemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
        'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
        'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
        'sachsen-anhalt', 'schleswig-holstein', 'thüringen'
    }

    if pd.isna(location):
        return locations

    try:
        # Split on common delimiters
        parts = re.split(r'[>/,\n]\s*', str(location))
        split_locations = []
        for part in parts:
            part = part.strip().lower()
            if part:
                # Further split by space if multiple states are concatenated
                words = part.split()
                temp = []
                current = ""
                for word in words:
                    if word in german_states:
                        if current:
                            temp.append(current.strip())
                        current = word
                    else:
                        current += " " + word if current else word
                if current:
                    temp.append(current.strip())
                split_locations.extend(temp)
        
        for loc in split_locations:
            loc = loc.strip().lower()
            if loc:
                if loc in german_states:
                    locations.add(loc.title())  # Capitalize for better geocoding
                else:
                    # Remove "region" and other common prefixes
                    clean_part = re.sub(r'^region\s+', '', loc)
                    if clean_part:
                        locations.add(clean_part.title())
    except Exception as e:
        logging.error(f"Error extracting location parts: {e}")

    return locations

def get_all_unique_locations(buyers_df, sellers_df):
    """Extract all unique locations from buyers and sellers dataframes."""
    unique_locations = set()

    for df, name in [(buyers_df, 'buyers'), (sellers_df, 'sellers')]:
        logging.info(f'Extracting locations from {name} dataframe...')
        for idx, location in df['location'].items():
            locations = _extract_location_parts(location)
            unique_locations.update(locations)

    logging.info(f'Total unique locations found: {len(unique_locations)}')
    return unique_locations

def geocode_locations(unique_locations, cache_path='geocode_cache.db'):
    """Geocode unique locations with caching."""
    geolocator = Nominatim(user_agent="buyer_seller_matching")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=10.0)

    # Ensure cache directory exists
    cache_dir = os.path.dirname(cache_path)
    if cache_dir and not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    with shelve.open(cache_path) as geocode_cache:
        for location in unique_locations:
            if location in geocode_cache:
                continue  # Already cached
            try:
                logging.info(f'Geocoding location: {location}')
                loc = geocode(location + ", Germany")
                if loc:
                    geocode_cache[location] = {'latitude': loc.latitude, 'longitude': loc.longitude}
                    logging.info(f'Geocoded {location}: ({loc.latitude}, {loc.longitude})')
                else:
                    geocode_cache[location] = {'latitude': None, 'longitude': None}
                    logging.warning(f'Geocoding failed for location: {location}')
            except Exception as e:
                logging.error(f"Geocoding error for location '{location}': {e}")
                geocode_cache[location] = {'latitude': None, 'longitude': None}

def update_dataframe_with_geocodes(df, cache_path='geocode_cache.db'):
    """Add latitude and longitude columns to the dataframe based on locations."""
    with shelve.open(cache_path) as geocode_cache:
        latitudes = []
        longitudes = []

        for idx, location in df['location'].items():
            locations = _extract_location_parts(location)
            lat_list = []
            lon_list = []
            for loc in locations:
                geocode_info = geocode_cache.get(loc, {'latitude': None, 'longitude': None})
                if geocode_info['latitude'] is not None and geocode_info['longitude'] is not None:
                    lat_list.append(geocode_info['latitude'])
                    lon_list.append(geocode_info['longitude'])
                else:
                    # If geocoding failed, append None
                    lat_list.append(None)
                    lon_list.append(None)
            # Convert lists to JSON strings for CSV compatibility
            latitudes.append(json.dumps(lat_list))
            longitudes.append(json.dumps(lon_list))

    df['latitude'] = latitudes
    df['longitude'] = longitudes
    return df

def main():
    # Paths to input and output files
    sellers_input_path = './data/branche_nexxt_change_sales_listings_nace.csv'
    sellers_output_path = './data/branche_nexxt_change_sales_listings_nace_geocoded.csv'

    buyers_input_path = './data/nexxt_change_purchase_listings.csv'
    buyers_output_path = './data/nexxt_change_purchase_listings_geocoded.csv'
    cache_path = './geocode_cache.db'

    # Load buyer and seller datasets
    logging.info('Loading buyer and seller datasets...')
    buyers_df = pd.read_csv(buyers_input_path)
    sellers_df = pd.read_csv(sellers_input_path)

    # Extract unique locations
    unique_locations = get_all_unique_locations(buyers_df, sellers_df)

    # Geocode locations with caching
    geocode_locations(unique_locations, cache_path=cache_path)

    # Update dataframes with geocodes
    logging.info('Updating buyers dataframe with geocodes...')
    buyers_df = update_dataframe_with_geocodes(buyers_df, cache_path=cache_path)

    logging.info('Updating sellers dataframe with geocodes...')
    sellers_df = update_dataframe_with_geocodes(sellers_df, cache_path=cache_path)

    # Save updated dataframes to new CSV files
    logging.info('Saving updated buyers dataframe...')
    buyers_df.to_csv(buyers_output_path, index=False)

    logging.info('Saving updated sellers dataframe...')
    sellers_df.to_csv(sellers_output_path, index=False)

    logging.info('Geocoding process completed successfully.')

if __name__ == "__main__":
    main()
