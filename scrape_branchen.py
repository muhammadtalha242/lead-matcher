import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    filename='scraping.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def scrape_branchen(url):
    """
    Fetches the 'branchen' information from the given URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The scraped 'branchen' value or None if not found.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the div containing the details
        detail_div = soup.find('div', class_='detail-item details-unternehmen rich-text')
        if not detail_div:
            logging.warning(f"Detail div not found at URL: {url}")
            return None

        # Find all dt tags within the detail div
        dt_tags = detail_div.find_all('dt')

        for dt in dt_tags:
            dt_text = dt.get_text(strip=True).lower()
            if 'branche' in dt_text:
                dd = dt.find_next_sibling('dd')
                if dd:
                    # Assuming the Branchen value is within a <li> tag inside <dd>
                    li = dd.find('li')
                    if li:
                        branchen_text = li.get_text(strip=True)
                        # Clean the text by replacing HTML entities and excessive whitespace
                        branchen_text = ' '.join(branchen_text.replace('&gt;', '>').split())
                        return branchen_text
                    else:
                        # If no <li>, get the text directly
                        branchen_text = dd.get_text(strip=True)
                        branchen_text = ' '.join(branchen_text.replace('&gt;', '>').split())
                        return branchen_text
        # If 'Branche' not found
        logging.warning(f"'Branche' not found at URL: {url}")
        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for URL {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error for URL {url}: {e}")
        return None

def main():
    input_csv = './data/data/nexxt_change_purchase_listings.csv'            # Replace with your input CSV file path
    output_csv = './data/data/nexxt_change_purchase_listings_update.csv'   # Output CSV with 'branchen' column updated

    # Read the CSV file
    try:
        df = pd.read_csv(input_csv, sep=",", dtype=str)
    except Exception as e:
        logging.critical(f"Failed to read CSV file {input_csv}: {e}")
        return

    # Ensure 'branchen' column exists
    if 'branchen' not in df.columns:
        df['branchen'] = None

    # Iterate over each row with a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
        url = row.get('url')
        if pd.isna(url) or not isinstance(url, str) or not url.strip():
            logging.warning(f"No valid URL at row {index}. Skipping.")
            continue

        # Skip if 'branchen' is already filled
        if pd.notna(row['branchen']) and row['branchen'].strip():
            continue

        branchen = scrape_branchen(url)
        if branchen:
            df.at[index, 'branchen'] = branchen
            logging.info(f"Scraped 'branchen' for URL {url}: {branchen}")
        else:
            logging.info(f"No 'branchen' found for URL {url}")

        # Be polite and avoid overwhelming the server
        time.sleep(1)  # Sleep for 1 second

    # Save the updated CSV
    try:
        df.to_csv(output_csv, index=False)
        logging.info(f"Updated CSV saved to {output_csv}")
        print(f"Updated CSV saved to {output_csv}")
    except Exception as e:
        logging.critical(f"Failed to write CSV file {output_csv}: {e}")

if __name__ == "__main__":
    main()

