# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd
# import time

# # Initialize WebDriver
# driver = webdriver.Chrome()
# driver.get("https://www.nexxt-change.org/SiteGlobals/Forms/Verkaufsangebot_Suche/Verkaufsangebotssuche_Formular.html")
# wait = WebDriverWait(driver, 10)

# # Accept cookies if prompted
# try:
#     wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "c-banner__button js-close-banner btn btn-primary"))).click()
# except:
#     pass

# # Data list to store extracted information
# data = []

# # Extract details function
# def extract_details():
#     try:
#         # Extracting details
#         title = driver.find_element(By.CSS_SELECTOR, ".inserat-details-box h1").text        
#         description = driver.find_element(By.XPATH, "//*[@id='inserat-detail']/p").text
#         cipher = driver.find_element(By.XPATH, "//dt[contains(text(),'Cipher')]/following-sibling::dd").text
#         date = driver.find_element(By.XPATH, "//*[@id='main']/div/div/div[2]/div/section[1]/div/dl/dd[1]").text
#         print("date: ",date)
#         # ad_type = driver.find_element(By.XPATH, "//dt[contains(text(),'Ad type')]/following-sibling::dd").text
#         # short_description = driver.find_element(By.CSS_SELECTOR, ".short-description p").text
#         # location = driver.find_element(By.XPATH, "//dt[contains(text(),'Location')]/following-sibling::dd/ul/li").text
#         # industry = driver.find_element(By.XPATH, "//dt[contains(text(),'Industries')]/following-sibling::dd/ul/li").text
#         # employees = driver.find_element(By.XPATH, "//dt[contains(text(),'Number of employees')]/following-sibling::dd").text
#         # turnover = driver.find_element(By.XPATH, "//dt[contains(text(),'Last annual turnover')]/following-sibling::dd").text
#         # price_range = driver.find_element(By.XPATH, "//dt[contains(text(),'Price range')]/following-sibling::dd").text
#         # expose = driver.find_element(By.XPATH, "//dt[contains(text(),'Expose')]/following-sibling::dd/a").get_attribute("href")
    
#         return {"Title": title}
#     except:
#         return None

# # Navigate through the first 100 listings
# for i in range(2):
#     try:
#         listings = driver.find_elements(By.CLASS_NAME, "inserat-list-item")
        
#         # Click on each listing to open and extract details
#         listing = listings[i].find_element(By.TAG_NAME, "a")
#         listing.click()
#         time.sleep(2)
        
#         # Extract and store data
#         details = extract_details()
#         print("details: ",details)
#         if details:
#             data.append(details)
        
#         # Return to listings page
#         driver.back()
#         time.sleep(2)
    
#     except Exception as e:
#         print(f"Error on listing {i}: {e}")
#         break

# # Save data to CSV
# df = pd.DataFrame(data)
# df.to_csv("nexxt_change_detailed_listings.csv", index=False)
# print("Data saved to nexxt_change_detailed_listings.csv")

# # Close the driver
# driver.quit()
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import csv
# from datetime import datetime
# import time

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # Run in headless mode
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
    
#     return webdriver.Chrome(options=options)
# # # Extract details function
# def extract_details(driver):
#     try:
#         # Extracting details
#         title = driver.find_element(By.CSS_SELECTOR, ".inserat-details-box h1").text        
#         description = driver.find_element(By.XPATH, "//*[@id='inserat-detail']/p").text
#         cipher = driver.find_element(By.XPATH, "//dt[contains(text(),'Cipher')]/following-sibling::dd").text
#         date = driver.find_element(By.XPATH, "//*[@id='main']/div/div/div[2]/div/section[1]/div/dl/dd[1]").text
#         print("date: ",date)
#         # ad_type = driver.find_element(By.XPATH, "//dt[contains(text(),'Ad type')]/following-sibling::dd").text
#         # short_description = driver.find_element(By.CSS_SELECTOR, ".short-description p").text
#         # location = driver.find_element(By.XPATH, "//dt[contains(text(),'Location')]/following-sibling::dd/ul/li").text
#         # industry = driver.find_element(By.XPATH, "//dt[contains(text(),'Industries')]/following-sibling::dd/ul/li").text
#         # employees = driver.find_element(By.XPATH, "//dt[contains(text(),'Number of employees')]/following-sibling::dd").text
#         # turnover = driver.find_element(By.XPATH, "//dt[contains(text(),'Last annual turnover')]/following-sibling::dd").text
#         # price_range = driver.find_element(By.XPATH, "//dt[contains(text(),'Price range')]/following-sibling::dd").text
#         # expose = driver.find_element(By.XPATH, "//dt[contains(text(),'Expose')]/following-sibling::dd/a").get_attribute("href")
    
#         return {"Title": title}
#     except:
#         return None

# def scrape_listings_from_page(driver):
#     listings = []
    
#     # Wait for listings to load
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "inserat-list-item"))
#     )
    
#     # Find all listing cards
#     cards = driver.find_elements(By.CLASS_NAME, "card")
    
#     for card in cards:
#         try:
#             # Extract the requested fields
#             date = card.find_element(By.CLASS_NAME, "date").text.strip()
            
#             title_element = card.find_element(By.CLASS_NAME, "card-title")
#             title = title_element.text.strip()
#             link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
#             try:
#                 shortDescription = card.find_element(By.CLASS_NAME, "inserat-teaser").text.strip()
#             except NoSuchElementException:
#                 description = ""
                
#             try:
#                 location = card.find_elements(By.CLASS_NAME, "card-topline--secondary")[-1].text.strip()
#             except (NoSuchElementException, IndexError):
#                 location = ""
            
#             listing_data = {
#                 'date': date,
#                 'title': title,
#                 'shortDescription': shortDescription,
#                 'location': location,
#                 'url': link
#             }
            
#             listings.append(listing_data)
#             print(f"Scraped: {title}")
            
#         except Exception as e:
#             print(f"Error scraping card: {str(e)}")
#             continue
            
#     return listings

# def get_total_pages(driver):
#     try:
#         pagination = driver.find_elements(By.CLASS_NAME, "pagination-item")
#         if pagination:
#             last_page = int(pagination[-2].text.strip())
#             return last_page
#     except Exception as e:
#         print(f"Error getting total pages: {str(e)}")
#     return 1

# def main():
#     driver = setup_driver()
#     base_url = "https://www.nexxt-change.org/SiteGlobals/Forms/Verkaufsangebot_Suche/Verkaufsangebotssuche_Formular.html"
#     all_listings = []
    
#     try:
#         # Visit main page
#         driver.get(base_url)
#         total_pages = get_total_pages(driver)
#         total_pages = 1
#         print(f"Found {total_pages} pages to scrape")
        
#         # Scrape each page
#         for page in range(1, total_pages + 1):
#             print(f"\nScraping page {page} of {total_pages}")
            
#             if page > 1:
#                 page_url = f"{base_url}?gtp=%252676d53c18-299c-4f55-8c88-f79ed3ce6d02_list%253D{page}"
#                 driver.get(page_url)
            
#             page_listings = scrape_listings_from_page(driver)
#             all_listings.extend(page_listings)
            
#             # Add a small delay between pages
#             time.sleep(2)
        
#         # Save results to CSV
#         filename = f"nexxt_change_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
#         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#             fieldnames = ['date', 'title', 'description', 'location', 'url']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
#             writer.writeheader()
#             for listing in all_listings:
#                 writer.writerow(listing)
                
#         print(f"\nScraping completed. {len(all_listings)} listings saved to {filename}")
        
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
        
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()


