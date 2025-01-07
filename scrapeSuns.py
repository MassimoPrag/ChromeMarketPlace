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

#Name, Price, Availibility, Size, Time, Link, Description
#aviability is true or false, true is availible, false is sold

def scrapeSuns():
    sunsUrl = "https://www.michaelsuns.com/?fbclid=PAZXh0bgNhZW0CMTEAAabcOmk-aXhHn49SDLGMzWNE0lOr1R54PKoRB0WjwdFv4IQneQoXfPCeZxk_aem_6KH8z7zeXWriaR_Ak2rEOA"
    driver = webdriver.Chrome(options=options)
    Brand, Name, Size, Price, Availible, Page, Link= [], [], [], [], [], [], []

    driver.get(sunsUrl)
    time.sleep(10)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='products-flex-container']//div[contains(@class, 'grid-item')]")))

    try:
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(7)
            new_height = driver.execute_script("return document.body.scrollHeight")


            listings = driver.find_elements(By.XPATH,"//div[@class='products-flex-container']//div[contains(@class, 'grid-item')]") # "//div[@class='products-flex-container']//div[contains(@class, 'grid-item')]"
            for i, listing in enumerate(listings):
                try:
                    name = listing.find_element(By.XPATH, './/div[@class="grid-title" and @data-test="plp-grid-title"]').text
                    price = listing.find_element(By.XPATH, './/div[@class="product-price"]').text
                    try:
                        availible = not listing.find_element(By.XPATH, './/div[@class="product-mark sold-out"]')
                    except NoSuchElementException:
                        availible = True
                    link = listing.find_element(By.XPATH, './/a[@class="grid-item-link product-lists-item"]').get_dom_attribute("href")                
                    link = f"https://www.michaelsuns.com{link}"
                    
                    size_match = re.search(r'\(([^)]+)\)', name)
                    if size_match:
                        size = size_match.group(1)
                        name = name.replace(size_match.group(0),'').strip()
                    else:
                        size = "N/A"
                    

                    
                    Name.append(name)
                    Price.append(price)
                    Availible.append(availible)
                    Link.append(link)
                    Size.append(size)
                    Brand.append("Chrome Hearts")
                    Page.append(1)

                except NoSuchElementException:
                    continue
            if new_height == last_height:
                break
            last_height = new_height
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        driver.quit()

    ItemDF=pd.DataFrame(zip(Brand,Name,Size,Price,Availible,Link),columns=['Brand', 'Name', 'Size', 'Price', 'Availible', 'Link'])

    # Remove rows that do not have the text "Chrome Hearts" in the name
    ItemDF = ItemDF[ItemDF['Name'].str.contains("Chrome Hearts")]

    # Remove "Chrome Hearts" from the name
    ItemDF['Name'] = ItemDF['Name'].str.replace("Chrome Hearts", "").str.strip()

    return ItemDF
#print(scrapeSuns())


