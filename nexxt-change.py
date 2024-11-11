from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
from datetime import datetime
import time

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
            # inserat_details = safe_find_element(driver, By.ID, "inserat-detail")
            detail_box = safe_find_element(driver, By.CLASS_NAME, "inserat-details-detail-box")
            # detail_box = inserat_details.find_element()
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

def scrape_listings_from_page(driver):
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
                
                if card_data['url']:  # Only proceed if we got a valid URL
                    # Get detailed information from the ad page
                    print(f"Scraping details for: {card_data['title']}")
                    details = scrape_ad_details(driver, card_data['url'])
                    
                    # Combine all information
                    listing_data = {
                        **card_data,
                        'long_description': details.get('long_description', ''),
                        'standort': '; '.join(details.get('Standort', '')),
                        'branchen': '; '.join(details.get('Branchen', [])),
                        'mitarbeiter': details.get('Anzahl Mitarbeiter', ''),
                        'jahresumsatz': details.get('Letzter Jahresumsatz', ''),
                        'preisvorstellung': details.get('Preisvorstellung', ''),
                        'international': details.get('Internationale Tätigkeit', '')
                    }
                    
                    listings.append(listing_data)
                    print(f"Successfully scraped: {card_data['title']}")
                    
                    # Add a small delay between ads
                    time.sleep(1.5)
                
            except Exception as e:
                print(f"Error processing card: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error processing page: {str(e)}")
    
    return listings

def get_total_pages(driver):
    try:
        pagination = driver.find_elements(By.CLASS_NAME, "pagination-item")
        if pagination:
            last_page = int(pagination[-2].text.strip())
            return last_page
    except Exception as e:
        print(f"Error getting total pages: {str(e)}")
    return 1

def main():
    driver = setup_driver()
    base_url = "https://www.nexxt-change.org/SiteGlobals/Forms/Verkaufsangebot_Suche/Verkaufsangebotssuche_Formular.html" # sales req
    # base_url = "https://www.nexxt-change.org/SiteGlobals/Forms/Kaufgesuch_Suche/Kaufgesuche_Formular.html" #purchase request
    all_listings = []
    
    try:
        # Visit main page
        driver.get(base_url)
        # total_pages = get_total_pages(driver)
        total_pages = 17
        print(f"Found {total_pages} pages to scrape")
        
        # Scrape each page
        for page in range(1, total_pages + 1):
            print(f"\nScraping page {page} of {total_pages}")
            
            if page > 1:
                page_url = f"{base_url}?gtp=%252676d53c18-299c-4f55-8c88-f79ed3ce6d02_list%253D{page}"
                driver.get(page_url)
            
            page_listings = scrape_listings_from_page(driver)
            all_listings.extend(page_listings)
            
            # Add a delay between pages
            time.sleep(2)
        
        # Save results to CSV
        filename = f"nexxt_change_sales_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # filename = f"nexxt_change_purchase_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'date', 'title', 'description', 'location', 'url',
                'long_description','standort', 'branchen', 'mitarbeiter', 'jahresumsatz',
                'preisvorstellung', 'international',
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for listing in all_listings:
                writer.writerow(listing)
                
        print(f"\nScraping completed. {len(all_listings)} listings saved to {filename}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()