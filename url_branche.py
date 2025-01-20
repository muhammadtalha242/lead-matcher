import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Usage example:
input_file = "./data/nexxt_change_sales_listings_udpate_branche.csv"      # CSV with a column named "URL"
output_file = './data/nexxt_change_sales_listings_udpate_branche.csv'
def get_branche_text(url):
    """
    Opens the URL in a Selenium-driven browser, 
    finds the 'Branche :' label, and extracts the associated text.
    Returns the extracted text or an empty string if not found.
    """
    # Initialize the Selenium driver (Chrome)
    # If you already have chromedriver in PATH, you could do:
    # driver = webdriver.Chrome()
    # Otherwise, webdriver_manager will install the correct version:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver= webdriver.Chrome(options=options)
    try:
        driver.get(url)
        
        # Method 1: Find <dt> containing text "Branche", then find sibling <dd>
        # XPATH Explanation:
        #   1) We look for any element whose text contains the word "Branche".
        #   2) Then we get the immediately following sibling <dd>.
        
        # Some sites might have leading/trailing spaces or slightly different text (like "Branche :"),
        # so we use 'contains(text(), "Branche")' rather than an exact match.
        element = driver.find_element(
            By.XPATH,
            "//*[contains(normalize-space(text()), 'Branche')]/following-sibling::dd[1]"
        )
        branche_text =  element.text.strip()

        return branche_text

    except (NoSuchElementException, TimeoutException):
        print(f"Could not find 'Branche :' text on page: {url}")
        return ""

    finally:
        driver.quit()


import pandas as pd
count = 2000
start =3500
end= start + count
data = pd.read_csv(input_file)[start:end]

for index, row in data.iterrows():
    url = row.get('url')
    start += 1
    print(f"{start} Processing: {url}")
    print(f"Pre Extracted Branche: {row.get('branchen')}")
    branche_text = get_branche_text(url)
    print(f"Extracted Branche: {branche_text}")
    if pd.isna(row.get('branchen')) :
        data.at[index, 'branchen'] = branche_text
    print(f"Post Extracted Branche: {data.at[index, 'branchen']}")
# Delete rows where branche_text is empty
data = data[data['branchen'] != '']
# Save the updated DataFrame to the output CSV
data.to_csv(f"./data/branche_nexxt_change_sales_listings_{start}_{end}.csv", index=False)