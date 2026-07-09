from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import os
import time

def scrape_pakwheels_listings():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    cars = []
    page = 1
    while True:
        url = f"https://www.pakwheels.com/used-cars/search/-/?page={page}"
        driver.get(url)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-listing-id]'))
            )
        except Exception as e:
            print(f"Timeout waiting for listings on page {page}: {e}")
            break
        time.sleep(2)  # Small extra wait for dynamic content
        listings = driver.find_elements(By.CSS_SELECTOR, 'li[data-listing-id]')
        print(f"Page {page}: Found {len(listings)} listings")
        if not listings:
            break
        # Debug: print HTML of first 3 listings on first page
        if page == 1:
            for idx, li in enumerate(listings[:3]):
                print(f"\n--- Listing {idx+1} HTML ---\n{li.get_attribute('outerHTML')}\n-------------------------\n")
        for li in listings:
            try:
                name = ''
                price = ''
                location = ''
                year = ''
                url = ''
                mileage = ''
                # Car name and detail URL (use .search-title a.car-name)
                a_tags = li.find_elements(By.CSS_SELECTOR, 'div.search-title a.car-name')
                if not a_tags:
                    continue  # skip if not found
                a_tag = a_tags[0]
                h3s = a_tag.find_elements(By.TAG_NAME, 'h3')
                if not h3s:
                    continue  # skip if no h3
                name = h3s[0].text.strip()
                url = a_tag.get_attribute('href')
                if url and url.startswith('/'):
                    url = 'https://www.pakwheels.com' + url
                # Try to extract year from name
                parts = name.split()
                if parts and parts[-2].isdigit() and len(parts[-2]) == 4:
                    year = parts[-2]
                elif parts and parts[-1].isdigit() and len(parts[-1]) == 4:
                    year = parts[-1]
                # Price (div.price-details)
                try:
                    price_div = li.find_element(By.CSS_SELECTOR, 'div.price-details')
                    price = price_div.text.strip()
                except:
                    price = ''
                # Location (ul.search-vehicle-info li)
                try:
                    loc_ul = li.find_element(By.CSS_SELECTOR, 'ul.search-vehicle-info')
                    loc_lis = loc_ul.find_elements(By.TAG_NAME, 'li')
                    if loc_lis:
                        location = loc_lis[0].text.strip()
                except:
                    location = ''
                # Mileage (ul.search-vehicle-info-2 li with 'km')
                try:
                    info2_ul = li.find_element(By.CSS_SELECTOR, 'ul.search-vehicle-info-2')
                    info2_lis = info2_ul.find_elements(By.TAG_NAME, 'li')
                    for li2 in info2_lis:
                        if 'km' in li2.text:
                            mileage = li2.text.strip()
                            break
                except:
                    mileage = ''
                if name:
                    cars.append({'name': name, 'year': year, 'price': price, 'location': location, 'url': url, 'mileage': mileage})
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue
        # Check for 'Next' button
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, 'ul.pagination li a[rel="next"]')
            if 'disabled' in next_btn.get_attribute('class'):
                break
        except NoSuchElementException:
            break
        page += 1
    driver.quit()
    df = pd.DataFrame(cars)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/pakwheels_listings.csv', index=False)
    print(f"Scraped {len(cars)} listings and saved to data/pakwheels_listings.csv")

if __name__ == "__main__":
    scrape_pakwheels_listings()
