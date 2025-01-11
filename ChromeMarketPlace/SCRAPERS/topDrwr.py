import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
from selenium.webdriver.chrome.options import Options
import random
import re

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-infobars')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

"""
Scrape top drwr which will already have a few sellers we dont end up scraping specifically
has alot of sold item data
"""

# https://topdrwr.io/all?brand=chrome%20hearts&brands=chrome%20hearts&page=2



def scrapeTD():
    driver = webdriver.Chrome(options=options)
    baseurl = "https://topdrwr.io/all?brand=chrome%20hearts&brands=chrome%20hearts&page=1"

    Brand, Name, Size, Price, Availible, Page, Link= [], [], [], [], [], [], []

    for i in range(1, 44):
        url = f"https://topdrwr.io/all?brand=chrome%20hearts&brands=chrome%20hearts&page={i}"
        driver.get(url)
        time.sleep(2)

        listings = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'grid') and contains(@class, 'gap-4')]/div"))
        )

        for listing in listings:
            try:
                name = listing.find_element(By.XPATH, ".//a[contains(@class, 'font-abcondbold') and contains(@class, 'leading-5')]").text
                Name.append(name)

                price = listing.find_element(By.XPATH, ".//p[contains(@class, 'text-lg') and contains(@class, 'font-semibold')]").text
                Price.append(price)

                link = listing.find_element(By.XPATH, ".//a[contains(@class, 'font-abcondbold') and contains(@class, 'leading-5')]").get_attribute("href")
                Link.append(link)

                size = listing.find_element(By.XPATH, ".//p[contains(@class, 'text-xs') and contains(@class, 'text-gray-400')]").text
                Size.append(size)

                brand = "Chrome Hearts"
                Brand.append(brand)

                Availible.append(True)

                Page.append(i)
            except NoSuchElementException:
                continue
        
    driver.quit()
    ItemDF = pd.DataFrame(zip(Brand, Name, Size, Price, Availible, Page, Link), columns=['Brand', 'Name', 'Size', 'Price', 'Availible', 'Page', 'Link'])
    return ItemDF

def clean_data(df):
    # Remove redundant "Chrome Hearts" from the "Brand" column
    df['Brand'] = df['Name'].apply(lambda x: 'Chrome Hearts' if 'Chrome Hearts' in x else x.split(' x ')[0])
    
    # Clean up the Name column
    df['Name'] = df['Name'].apply(lambda x: x.replace('Chrome Hearts', '').replace(' x ', '').strip())
    
    return df

def main():
    x = scrapeTD()
    x = clean_data(x)
    
    x.to_csv("topDrwr.csv", index=False)

if __name__ == "__main__":
    main()





