# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException

# def handle_cookie_modal(driver):
#     try:
#         # 1. Wait for the cookie consent container to appear
#         cookie_modal = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "cookie-consent"))
#         )
        
#         # 2. Within this container, locate the "Refuse" button
#         #    (class="deny btn btn--secondary")
#         refuse_button = cookie_modal.find_element(
#             By.XPATH,
#             ".//button[@class='deny btn btn--secondary']"
#         )
        
#         # 3. Click the "Refuse" button
#         refuse_button.click()
        
#         # 4. Optionally wait a moment for the modal to disappear
#         WebDriverWait(driver, 5).until(
#             EC.invisibility_of_element_located((By.ID, "cookie-consent"))
#         )
        
#         print("Cookie modal dismissed successfully.")
#     except TimeoutException:
#         print("Cookie modal not found or not loaded in time.")
#     except NoSuchElementException:
#         print("Cookie refusal button not found.")

# def scrape_dub():
#     """
#     1. Start on the DUB main listings page.
#     2. Loop through all ads on each page.
#     3. For each ad, open the detail link in a new tab, scrape data, then close the tab.
#     4. Click the 'Next' pagination button (a <button> under <li class="next">).
#     5. Stop when there is no next button.
#     6. Return a list of dicts with the extracted data.
#     """

#     # ---------------------------
#     # 1. SETUP SELENIUM
#     # ---------------------------
#     options = webdriver.ChromeOptions()
#     # Uncomment this to run headless (no browser GUI):
#     options.add_argument("--headless")
#     options.add_argument("--start-maximized")
#     driver = webdriver.Chrome(options=options)

#     # Starting URL (main listings)
#     start_url = (
#         "https://www.dub.de/unternehmen-kaufen/"
#         "?tx_enterprisermarket_searchoffer%5Baction%5D=index"
#         "&tx_enterprisermarket_searchoffer%5Bcontroller%5D=SearchOffer"
#         "&cHash=f99f9de658b333f0c2164b6b5902485b"
#     )
#     driver.get(start_url)

#     # Optional: Handle cookie banner here if needed
#     try:
#         handle_cookie_modal(driver)
#     except Exception as e:
#         print(f"Error handling cookie modal: {e}")


#     all_data = []
#     page_number = 1

#     # ---------------------------
#     # 2. PAGINATION LOOP
#     # ---------------------------
#     while True:
#         print(f"\nScraping page {page_number}...")

#         # Wait for the listings container (to be sure page is loaded)
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[@class='row row-cols-1 row-cols-md-2 g-4']")
#                 )
#             )
#         except TimeoutException:
#             print("Could not find listings container. Stopping.")
#             break

#         # ---------------------------
#         # 3. FIND ALL AD CARDS ON THIS PAGE
#         # ---------------------------
#         cards = driver.find_elements(
#             By.XPATH,
#             ".//div[@class='row row-cols-1 row-cols-md-2 g-4']/div[@class='col']"
#         )
#         if not cards:
#             print("No cards found on this page. Stopping.")
#             break

#         # ---------------------------
#         # 4. FOR EACH CARD, OPEN DETAIL PAGE AND SCRAPE
#         # ---------------------------
#         for card in cards:
#             try:
#                 link_element = card.find_element(By.XPATH, ".//a[contains(@class, 'content-hub__teaser-link')]")
#                 detail_url = link_element.get_attribute("href")
#             except NoSuchElementException:
#                 continue  # Skip if no link

#             # 4a. Open detail page in a new tab
#             driver.execute_script("window.open('');")
#             driver.switch_to.window(driver.window_handles[-1])
#             driver.get(detail_url)

#             # Let the detail page load
#             time.sleep(2)

#             # 4b. SCRAPE DATA FROM DETAIL PAGE
#             ad_data = scrape_detail_page(driver, detail_url)

#             # 4c. ADD to all_data
#             all_data.append(ad_data)

#             # 4d. Close the detail tab & go back to the main tab
#             driver.close()
#             driver.switch_to.window(driver.window_handles[0])

#         # ---------------------------
#         # 5. CLICK THE NEXT BUTTON IF IT EXISTS
#         # ---------------------------
#         # The next-page button is inside <li class="next"> <button ... >
#         # If it doesn't exist, we're on the last page.
#         try:
#             next_button = driver.find_element(
#                 By.XPATH,
#                 "//ul[@class='f3-widget-paginator pagination']/li[@class='next']/button"
#             )
#             print("Next button found.", next_button)
#             # Scroll into view
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
#             time.sleep(1)  # Let the scrolling animation settle

#             # Click after scrolling
#             next_button.click()
#             page_number += 1
#             time.sleep(2)  # Wait for the next page to load
#         except NoSuchElementException:
#             print("No next button found. Probably the last page. Stopping.")
#             break

#     # ---------------------------
#     # 6. DONE: CLOSE AND RETURN
#     # ---------------------------
#     driver.quit()
#     return all_data


# def scrape_detail_page(driver, detail_url):
#     """
#     Given a Selenium WebDriver already on a detail page,
#     extract the requested data using XPath.

#     Returns a dict with:
#     - Title
#     - Region
#     - Branchen
#     - Anforderungen an den Käufer
#     - Beschreibung des Verkaufsangebots
#     - Detail URL
#     """

#     # 1. TITEL: <h1> inside <div class="single singleOffer default">
#     try:
#         title_elem = driver.find_element(By.XPATH, "//div[@class='single singleOffer default']//h1")
#         title = title_elem.text.strip()
#     except NoSuchElementException:
#         title = ""

#     # 2. REGION: from the RIGHT-hand list-group item with label "Region"
#     try:
#         region_li = driver.find_element(
#             By.XPATH,
#             "//li[div[@class='ms-2 me-auto']/div[@class='fw-bold' and text()='Region']]"
#         )
#         li_text = region_li.text.strip().split("\n", 1)
#         region = li_text[1].strip() if len(li_text) > 1 else ""
#     except NoSuchElementException:
#         region = ""

#     # 3. BRANCHEN: under "Keyfacts" -> "Branchen"
#     try:
#         branchen_li = driver.find_element(
#             By.XPATH,
#             "//li[.//div[@class='fw-bold' and text()='Branchen']]"
#         )
#         branchen_items = branchen_li.find_elements(By.XPATH, ".//ul/li")
#         branchen_list = [bi.text.strip() for bi in branchen_items]
#         branchen = ", ".join(branchen_list)
#     except NoSuchElementException:
#         branchen = ""

#     # 4. ANFORDERUNGEN AN DEN KÄUFER: also in Keyfacts
#     try:
#         anforderungen_li = driver.find_element(
#             By.XPATH,
#             "//li[.//div[@class='fw-bold' and contains(text(),'Anforderungen an den Käufer')]]"
#         )
#         anforderungen_text = anforderungen_li.text.strip().split("\n", 1)
#         anforderungen = anforderungen_text[1].strip() if len(anforderungen_text) > 1 else ""
#     except NoSuchElementException:
#         anforderungen = ""

#     # 5. BESCHREIBUNG DES VERKAUFSANGEBOTS
#     try:
#         beschreibung_container = driver.find_element(
#             By.XPATH,
#             "//div[@class='col-xl-8'][h2[span[text()='Beschreibung des Verkaufsangebots']]]"
#         )
#         raw_text = beschreibung_container.text.strip()
#         lines = raw_text.splitlines()
#         if lines and "Beschreibung des Verkaufsangebots" in lines[0]:
#             beschreibung = "\n".join(lines[1:]).strip()
#         else:
#             beschreibung = raw_text
#     except NoSuchElementException:
#         beschreibung = ""

#     return {
#         "Title": title,
#         "Region": region,
#         "Branchen": branchen,
#         "Anforderungen an den Käufer": anforderungen,
#         "Beschreibung des Verkaufsangebots": beschreibung,
#         "Detail URL": detail_url
#     }


# if __name__ == "__main__":
#     scraped_data = scrape_dub()
#     print(f"\nScraping complete. Found {len(scraped_data)} ads in total.")

#     # Print a sample of the results
#     for i, ad in enumerate(scraped_data[:3], start=1):
#         print(f"\n--- Ad #{i} ---")
#         for k, v in ad.items():
#             print(f"{k}: {v}")
import pandas as pd
import logging
from typing import List, Dict, Set, Tuple
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)
import csv
import time
import hashlib

# Set up logging (optional)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 1. DRIVER SETUP
# -----------------------------------------------------------------------------
def setup_driver():
    """Set up the Chrome WebDriver with required options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # run without opening a GUI
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--start-maximized')  # If needed, uncomment

    return webdriver.Chrome(options=options)

# -----------------------------------------------------------------------------
# 2. COOKIE MODAL HANDLING
# -----------------------------------------------------------------------------
def handle_cookie_modal(driver):
    """
    Dismisses the cookie consent modal by clicking the 'Refuse' button
    if it appears (id="cookie-consent" and class="deny btn btn--secondary").
    """
    try:
        # Wait for the cookie-consent container to appear (up to 10s)
        cookie_modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cookie-consent"))
        )
        logger.info("Cookie modal found. Attempting to click 'Refuse'.")

        # Locate the 'Refuse' button
        refuse_button = cookie_modal.find_element(
            By.XPATH,
            ".//button[@class='deny btn btn--secondary']"
        )
        refuse_button.click()

        # Wait for the modal to disappear
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "cookie-consent"))
        )
        logger.info("Cookie modal dismissed successfully.")

    except TimeoutException:
        logger.info("Cookie modal not found or not loaded in time (Timeout).")
    except NoSuchElementException:
        logger.info("Refuse button not found inside cookie modal.")
    except ElementClickInterceptedException as e:
        logger.warning(f"Cookie modal button click intercepted: {e}")

# -----------------------------------------------------------------------------
# 3. APPLY FILTERS (CHECK 'DEUTSCHLAND')
# -----------------------------------------------------------------------------
def apply_filter(driver):
    """
    Ensures 'Deutschland' is checked and unchecks other countries if necessary,
    then clicks the 'Suchen' or filter button (if present).
    """
    time.sleep(1)

    # 1. Expand the "Land" accordion if needed
    try:
        land_accordion_button = driver.find_element(By.XPATH, "//button[@data-bs-target='#flush-collapseCountry']")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", land_accordion_button)
        time.sleep(1)
        # If it’s not already expanded, click it:
        if "collapsed" in land_accordion_button.get_attribute("class"):
            land_accordion_button.click()
            time.sleep(1)
    except NoSuchElementException:
        logger.info("No 'Land' accordion button found. Possibly it's already visible.")

    # 2. Ensure 'Deutschland' is checked
    try:
        de_checkbox = driver.find_element(By.ID, "country_3")
        if not de_checkbox.is_selected():
            de_checkbox.click()
            time.sleep(0.5)
        logger.info("Deutschland checkbox is now selected.")
    except NoSuchElementException:
        logger.error("Could not find 'Deutschland' checkbox (id='country_3').")

    # Optionally: Uncheck other countries so only 'Deutschland' remains
    # other_country_ids = ["4","5","11","10","6","12","7","9","8"]
    # for c_id in other_country_ids:
    #     try:
    #         other_box = driver.find_element(By.ID, f"country_{c_id}")
    #         if other_box.is_selected():
    #             other_box.click()
    #             time.sleep(0.3)
    #     except NoSuchElementException:
    #         pass

    # 3. If there's a 'Suchen' or filter button, click it
    try:
        search_button = driver.find_element(By.XPATH, "//input[@type='submit' and contains(@value,'Suchen')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
        time.sleep(1)
        search_button.click()
        logger.info("Clicked the 'Suchen' button to apply the filter.")
        time.sleep(2)
    except NoSuchElementException:
        logger.info("'Suchen' button not found. Possibly the filter updates automatically.")

# -----------------------------------------------------------------------------
# SAFE GET TEXT, FIND ELEMENT, ETC...
# -----------------------------------------------------------------------------
def safe_get_text(element, default=""):
    try:
        return element.text.strip()
    except (StaleElementReferenceException, NoSuchElementException):
        return default

def safe_find_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except (TimeoutException, NoSuchElementException):
        return None

# -----------------------------------------------------------------------------
# SCRAPE DETAIL PAGE
# -----------------------------------------------------------------------------
def scrape_detail_page(driver, detail_url):
    """Same logic as before – opens new tab, scrapes detail info, closes tab."""
    try:
        main_window = driver.current_window_handle
        driver.execute_script(f"window.open('{detail_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        # 1. TITLE
        try:
            title_elem = driver.find_element(By.XPATH, "//div[@class='single singleOffer default']//h1")
            title = title_elem.text.strip()
        except NoSuchElementException:
            title = ""

        # 2. REGION
        try:
            region_li = driver.find_element(
                By.XPATH,
                "//li[div[@class='ms-2 me-auto']/div[@class='fw-bold' and text()='Region']]"
            )
            li_text = region_li.text.strip().split("\n", 1)
            region = li_text[1].strip() if len(li_text) > 1 else ""
        except NoSuchElementException:
            region = ""

        # 3. BRANCHEN
        try:
            branchen_li = driver.find_element(
                By.XPATH,
                "//li[.//div[@class='fw-bold' and text()='Branchen']]"
            )
            branchen_items = branchen_li.find_elements(By.XPATH, ".//ul/li")
            branchen_list = [bi.text.strip() for bi in branchen_items]
            branchen = ", ".join(branchen_list)
        except NoSuchElementException:
            branchen = ""

        # 4. ANFORDERUNGEN AN DEN KÄUFER
        try:
            anforderungen_li = driver.find_element(
                By.XPATH,
                "//li[.//div[@class='fw-bold' and contains(text(),'Anforderungen an den Käufer')]]"
            )
            anforderungen_text = anforderungen_li.text.strip().split("\n", 1)
            anforderungen = anforderungen_text[1].strip() if len(anforderungen_text) > 1 else ""
        except NoSuchElementException:
            anforderungen = ""

        # 5. BESCHREIBUNG DES VERKAUFSANGEBOTS
        try:
            beschreibung_container = driver.find_element(
                By.XPATH,
                "//div[@class='col-xl-8'][h2[span[text()='Beschreibung des Verkaufsangebots']]]"
            )
            raw_text = beschreibung_container.text.strip()
            lines = raw_text.splitlines()
            if lines and "Beschreibung des Verkaufsangebots" in lines[0]:
                beschreibung = "\n".join(lines[1:]).strip()
            else:
                beschreibung = raw_text
        except NoSuchElementException:
            beschreibung = ""

        detail_data = {
            "Title": title,
            "Region": region,
            "Branchen": branchen,
            "Anforderungen an den Käufer": anforderungen,
            "Beschreibung des Verkaufsangebots": beschreibung,
            "Detail URL": detail_url
        }

        driver.close()
        driver.switch_to.window(main_window)
        return detail_data

    except Exception as e:
        logger.error(f"Error handling ad page {detail_url}: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return {}

# -----------------------------------------------------------------------------
# EXTRACT CARD DATA
# -----------------------------------------------------------------------------
def extract_card_data(card):
    data = {
        "Title": "",
        "Region": "",
        "Branchen": "",
        "Anforderungen an den Käufer": "",
        "Beschreibung des Verkaufsangebots": "",
        "Detail URL": ""
    }
    try:
        link_element = card.find_element(By.XPATH, ".//a[contains(@class, 'content-hub__teaser-link')]")
        detail_url = link_element.get_attribute("href")
        data["Detail URL"] = detail_url
    except NoSuchElementException:
        pass
    return data

# -----------------------------------------------------------------------------
# GENERATE HASH
# -----------------------------------------------------------------------------
def generate_hash(data):
    combined_data = (
        f"{data.get('Title','')}{data.get('Region','')}{data.get('Branchen','')}"
        f"{data.get('Anforderungen an den Käufer','')}{data.get('Beschreibung des Verkaufsangebots','')}"
        f"{data.get('Detail URL','')}"
    )
    return hashlib.sha256(combined_data.encode('utf-8')).hexdigest()

# -----------------------------------------------------------------------------
# SCRAPE LISTINGS FROM PAGE
# -----------------------------------------------------------------------------
def scrape_listings_from_page(driver, existing_hashes):
    listings = []
    duplicate_found = False

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='row row-cols-1 row-cols-md-2 g-4']")
            )
        )
    except TimeoutException:
        logger.info("No listings container found on this page.")
        return listings, duplicate_found

    cards = driver.find_elements(By.XPATH, ".//div[@class='row row-cols-1 row-cols-md-2 g-4']/div[@class='col']")
    if not cards:
        logger.info("No cards found on this page.")
        return listings, duplicate_found

    for card in cards:
        try:
            card_data = extract_card_data(card)
            detail_url = card_data.get("Detail URL", "")
            if not detail_url:
                continue

            detail_data = scrape_detail_page(driver, detail_url)
            combined_data = {**card_data, **detail_data}  # merges fields
            listing_hash = generate_hash(combined_data)

            if listing_hash in existing_hashes:
                logger.info(f"Duplicate found. Stopping. URL={detail_url}")
                duplicate_found = True
                break

            listings.append(combined_data)
            existing_hashes.add(listing_hash)

            logger.info(f"Scraped listing: {combined_data.get('Title','(No Title)')} => {detail_url}")
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"Error processing card: {e}")
            continue

    return listings, duplicate_found

# -----------------------------------------------------------------------------
# LOAD EXISTING DATA
# -----------------------------------------------------------------------------
def load_existing_data(filename):
    hashes = set()
    try:
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            row_data = {
                "Title": row.get("Title", ""),
                "Region": row.get("Region", ""),
                "Branchen": row.get("Branchen", ""),
                "Anforderungen an den Käufer": row.get("Anforderungen an den Käufer", ""),
                "Beschreibung des Verkaufsangebots": row.get("Beschreibung des Verkaufsangebots", ""),
                "Detail URL": row.get("Detail URL", ""),
            }
            listing_hash = generate_hash(row_data)
            hashes.add(listing_hash)
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Error loading existing data: {e}")
    return hashes

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    filename = "./data/dub_listings.csv"
    all_listings = []
    start_page = 1
    total_pages = 50

    driver = setup_driver()
    existing_hashes = load_existing_data(filename)

    try:
        start_url = (
            "https://www.dub.de/unternehmen-kaufen/"
            "?tx_enterprisermarket_searchoffer%5Baction%5D=index"
            "&tx_enterprisermarket_searchoffer%5Bcontroller%5D=SearchOffer"
            "&cHash=f99f9de658b333f0c2164b6b5902485b"
        )
        driver.get(start_url)

        # 1. Handle cookie modal
        handle_cookie_modal(driver)

        # 2. Apply filter (Deutschland, etc.)
        apply_filter(driver)

        # 3. Now scrape multiple pages
        current_page = start_page
        pages_scraped = 0

        while pages_scraped < total_pages:
            logger.info(f"Scraping page {current_page}...")

            page_listings, duplicate_found = scrape_listings_from_page(driver, existing_hashes)
            all_listings.extend(page_listings)
            pages_scraped += 1

            if duplicate_found:
                break
            if pages_scraped >= total_pages:
                logger.info(f"Reached total_pages={total_pages}. Stopping.")
                break

            # Try next-page button
            try:
                next_button = driver.find_element(
                    By.XPATH,
                    "//ul[@class='f3-widget-paginator pagination']/li[@class='next']/button"
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                time.sleep(1)
                next_button.click()
                time.sleep(2)
                current_page += 1
            except NoSuchElementException:
                logger.info("No next button found. Probably last page.")
                break

        # 4. Save to CSV
        if all_listings:
            fieldnames = [
                "Title",
                "Region",
                "Branchen",
                "Anforderungen an den Käufer",
                "Beschreibung des Verkaufsangebots",
                "Detail URL",
            ]
            with open(filename, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if csvfile.tell() == 0:
                    writer.writeheader()
                for listing in all_listings:
                    writer.writerow(listing)
            logger.info(f"{len(all_listings)} new listings appended to {filename}")
        else:
            logger.info("No new listings to append.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
