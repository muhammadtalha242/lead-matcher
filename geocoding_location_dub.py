import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

def main():
    # -------------------------------------------------------------------------
    # 1. Settings
    # -------------------------------------------------------------------------
    input_csv = "./data/dub_listings.csv"         # Name of your input CSV
    output_csv = "./data/dub_listings_geo.csv"    # Name of your output CSV
    region_column = "Region"               # Column with textual location info
    
    # -------------------------------------------------------------------------
    # 2. Read the CSV
    # -------------------------------------------------------------------------
    df = pd.read_csv(input_csv)
    
    # If "Region" is missing, handle gracefully
    if region_column not in df.columns:
        print(f"Error: '{region_column}' column not found in {input_csv}")
        return
    
    # -------------------------------------------------------------------------
    # 3. Setup Geopy / Nominatim
    # -------------------------------------------------------------------------
    # Create the geolocator using Nominatim
    geolocator = Nominatim(user_agent="my_geo_script")

    # Create a rate-limited geocoder (to avoid hitting usage limits too quickly)
    geocode_with_delay = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Create columns for lat/lon if they don't exist
    if "Latitude" not in df.columns:
        df["Latitude"] = None
    if "Longitude" not in df.columns:
        df["Longitude"] = None
    
    # -------------------------------------------------------------------------
    # 4. Cache to avoid re-geocoding the same region multiple times
    # -------------------------------------------------------------------------
    geo_cache = {}
    
    # -------------------------------------------------------------------------
    # 5. Loop through each row & geocode
    # -------------------------------------------------------------------------
    for idx, row in df.iterrows():
        region_name = str(row[region_column]).strip()
        
        # Skip if region is empty
        if not region_name:
            continue
        
        # Check if we already have it in cache
        if region_name in geo_cache:
            lat, lon = geo_cache[region_name]
        else:
            # Perform the geocoding
            try:
                location = geocode_with_delay(region_name)
                if location is not None:
                    lat, lon = (location.latitude, location.longitude)
                else:
                    lat, lon = (None, None)
            except Exception as e:
                print(f"Geocoding error for '{region_name}': {e}")
                lat, lon = (None, None)
            
            # Store in cache
            geo_cache[region_name] = (lat, lon)
        
        # Update the DataFrame
        df.at[idx, "Latitude"] = lat
        df.at[idx, "Longitude"] = lon
        
        # Optional: print progress
        print(f"[{idx}] {region_name} => {lat}, {lon}")
    
    # -------------------------------------------------------------------------
    # 6. Write out the updated CSV
    # -------------------------------------------------------------------------
    df.to_csv(output_csv, index=False)
    print(f"\nGeocoding complete! File saved as: {output_csv}")

if __name__ == "__main__":
    main()
