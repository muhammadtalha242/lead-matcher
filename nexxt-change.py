import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
import time
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    return webdriver.Chrome(options=options)

def safe_get_text(element, default=""):
    """Safely get text from an element with error handling"""
    try:
        return element.text.strip()
    except (StaleElementReferenceException, NoSuchElementException):
        return default

def safe_find_element(driver, by, value, timeout=10):
    """Safely find an element with explicit wait"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except (TimeoutException, NoSuchElementException):
        return None

def scrape_ad_details(driver, url):
    """Scrape detailed information from individual ad page"""
    try:
        # Store current window handle
        main_window = driver.current_window_handle
        
        # Open link in new tab
        driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        
        # Wait for details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "detail-item"))
        )
        
        details = {}
        
        try:
            # Get Beschreibung content
            detail_box = safe_find_element(driver, By.CLASS_NAME, "inserat-details-detail-box")
            if detail_box:
                beschreibung_elements = detail_box.find_elements(By.TAG_NAME, "p")
                beschreibung_text = "\n".join([safe_get_text(elem) for elem in beschreibung_elements])
                details['long_description'] = beschreibung_text

            # Find the company details section
            company_section = safe_find_element(driver, By.CLASS_NAME, "details-unternehmen")
            if company_section:
                # Get all definition lists
                dl_elements = company_section.find_elements(By.TAG_NAME, "dl")
                
                for dl in dl_elements:
                    # Get all dt (terms) and dd (descriptions) elements
                    dts = dl.find_elements(By.TAG_NAME, "dt")
                    dds = dl.find_elements(By.TAG_NAME, "dd")
                    
                    for dt, dd in zip(dts, dds):
                        # Clean up the key (remove colon and extra spaces)
                        key = safe_get_text(dt).rstrip(':').strip()
                        
                        # Handle lists (like Branchen/Industries)
                        list_items = dd.find_elements(By.TAG_NAME, "li")
                        if list_items:
                            value = [safe_get_text(item) for item in list_items]
                        else:
                            value = safe_get_text(dd)
                        
                        if key:  # Only add if we got a valid key
                            details[key] = value
        
        except Exception as e:
            print(f"Error extracting details from ad page: {str(e)}")
        
        # Close the tab and switch back to main window
        driver.close()
        driver.switch_to.window(main_window)
        
        return details
        
    except Exception as e:
        print(f"Error handling ad page {url}: {str(e)}")
        # Make sure we're back on the main window
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return {}

def extract_card_data(card):
    """Extract data from a single card with error handling"""
    data = {
        'date': '',
        'title': '',
        'description': '',
        'location': '',
        'url': ''
    }
    
    try:
        # Extract date
        date_elem = card.find_element(By.CLASS_NAME, "date")
        data['date'] = safe_get_text(date_elem)
        
        # Extract title and URL
        title_element = card.find_element(By.CLASS_NAME, "card-title")
        data['title'] = safe_get_text(title_element)
        link_elem = title_element.find_element(By.TAG_NAME, "a")
        data['url'] = link_elem.get_attribute("href")
        
        # Extract description
        try:
            desc_elem = card.find_element(By.CLASS_NAME, "inserat-teaser")
            data['description'] = safe_get_text(desc_elem)
        except NoSuchElementException:
            pass
            
        # Extract location
        try:
            location_elements = card.find_elements(By.CLASS_NAME, "card-topline--secondary")
            if location_elements:
                data['location'] = safe_get_text(location_elements[-1])
        except NoSuchElementException:
            pass
            
    except Exception as e:
        print(f"Error extracting card data: {str(e)}")
    
    return data

def generate_hash(data):
    """Generate a hash of the combined fields for duplicate detection"""
    combined_data = f"{data['date']}{data['title']}{data['description']}{data['location']}{data['url']}"
    return hashlib.sha256(combined_data.encode('utf-8')).hexdigest()

def scrape_listings_from_page(driver, existing_hashes):
    listings = []
    
    try:
        # Wait for listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inserat-list-item"))
        )
        
        # Find all listing cards
        cards = driver.find_elements(By.CLASS_NAME, "card")
        
        for card in cards:
            try:
                # Extract basic information from card
                card_data = extract_card_data(card)
                # if card_data['url']:
                # Generate hash for duplicate detection
                listing_hash = generate_hash(card_data)
                
                # Stop scraping if we find a duplicate hash
                if listing_hash in existing_hashes:
                    print("Duplicate found. Stopping further scraping.")
                    print(f"Duplicate URL: {card_data['url']}")
                    return listings, True
                
                # Get detailed information from the ad page
                print(f"Scraping details for: {card_data['title']}")
                details = scrape_ad_details(driver, card_data['url'])
                # Combine all information
                listing_data = {
                    **card_data,
                    'long_description': details.get('long_description', ''),
                    'standort': '; '.join(details.get('Standort', '')),
                    # 'branchen': '; '.join(details.get('Branchen', [])),
                    'branchen': '; '.join(details.get('Branchen', '') if details.get('Branchen', '') else details.get('Branche', '')),
                    'mitarbeiter': details.get('Anzahl Mitarbeiter', ''),
                    'jahresumsatz': details.get('Letzter Jahresumsatz', ''),
                    'preisvorstellung': details.get('Preisvorstellung', ''),
                    'international': details.get('Internationale Tätigkeit', '')
                }
                listings.append(listing_data)
                print(f"Successfully scraped: {card_data['title']} => {card_data['date']}")
                
                # Add a small delay between ads
                time.sleep(1.5)
                
            except Exception as e:
                print(f"Error processing card: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error processing page: {str(e)}")
    
    return listings, False

def load_existing_data(filename):
    """Load existing data from the CSV file to avoid duplicates"""
    try:
        df = pd.read_csv(filename)
        hashes = set()
        for _, row in df.iterrows():
            combined_data = f"{row['date']}{row['title']}{row['description']}{row['location']}{row['url']}"
            listing_hash = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
            hashes.add(listing_hash)
        return hashes
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        return set()

def main():
    driver = setup_driver()
    base_url = "https://www.nexxt-change.org/SiteGlobals/Forms/Verkaufsangebot_Suche/Verkaufsangebotssuche_Formular.html" # sales req
    # base_url = "https://www.nexxt-change.org/SiteGlobals/Forms/Kaufgesuch_Suche/Kaufgesuche_Formular.html" #purchase request
    filename = "./data/branche_nexxt_change_sales_listings_scrape.csv"
    # filename = "./data/nexxt_change_purchase_listings.csv"
    all_listings = []
    
    # Load existing data to avoid duplicates
    if filename:
        existing_hashes = load_existing_data(filename)
    else: 
        existing_hashes = set()
    try:
        #LAST SCAPPED TILL: 318
        # Visit main page
        driver.get(base_url)
        total_pages = 80
        start_page = 1
        print(f"Found {total_pages} pages to scrape")
        
        # Scrape each page
        for page in range(start_page, start_page+total_pages):
            print(f"\nScraping page {page} of {start_page+total_pages}")
            
            if page > 1:
                page_url = f"{base_url}?gtp=%252676d53c18-299c-4f55-8c88-f79ed3ce6d02_list%253D{page}" # sales page
                # page_url = f"{base_url}?gtp=%252686eb08f2-8f72-4780-a40b-049454c7eccf_list%253D{page}"   # purchase page

                driver.get(page_url)
            
            page_listings, duplicate_found = scrape_listings_from_page(driver, existing_hashes)
            all_listings.extend(page_listings)
            
            # Stop scraping if a duplicate is found
            if duplicate_found:
                break
            
            # Add a delay between pages
            time.sleep(2)
        
        # Save results to CSV
        if all_listings:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'date', 'title', 'description', 'location', 'url',
                    'long_description','standort', 'branchen', 'mitarbeiter', 'jahresumsatz',
                    'preisvorstellung', 'international',
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write only if the file is new
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                for listing in all_listings:
                    writer.writerow(listing)
                    
            print(f"\nScraping completed. {len(all_listings)} new listings appended to {filename}")
        else:
            print("\nNo new listings found to append.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
