"""
Go through the website
all items are for sale, all sold items are not priced

Standard DF

Name, Price, Availibility, Size, Time, Link, Description
add avilibility column, true is availible, false is sold
Common designer: chrome hearts, need to make sold as boolean or yes/no str
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.chrome.options import Options
import random

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


def scrapeJR():
    #base_url = https://justinreed.com/collections/chrome-hearts 
    # https://justinreed.com/collections/chrome-hearts?page=2

    base = "https://justinreed.com/collections/chrome-hearts"



    driver = webdriver.Chrome(options=options)



    #looping throuh all listing items 


    #establish lists
    Brand, Name, Size, Price, Availible, Page, Link = [], [], [], [], [], [], []

    #get all items info, name, price, size, timeunavail(emty col), link, description(go into item)

    for i in range(1,20):
        pgURL = f"{base}?page={i}"
        driver.get(pgURL)
        time.sleep(3)

        listings = driver.find_elements(By.XPATH,"//div[@id='products']/div[@class='row g-0']/div[@class='col-6 col-lg-4 px-lg-3 px-2']")
        len(listings)

        for listing in listings:
            Page.append(i)
            Brand.append("Chrome Hearts")
            name = listing.find_element(By.XPATH, ".//div[@class='sohne-buch-13 mb-3']/a").text.strip()
            Name.append(name)

            price = listing.find_element(By.XPATH,".//span[@class='money']").text
            Price.append(price)

            try:
                listing.find_element(By.XPATH, ".//div[contains(@class, 'sohne-buch-10') and contains(text(), 'Sold Out')]")
                availible = False
            except NoSuchElementException:
                availible = True

            Availible.append(availible)
            link_element = listing.find_element(By.XPATH,".//div[@class='product']/a").get_dom_attribute("href")
            linkHref = f"https://justinreed.com{link_element}"
            Link.append(linkHref)
            size = listing.find_element(By.XPATH, ".//div[@class='mb-3']").text


            Size.append(size)

    driver.quit()
    ItemDF=pd.DataFrame(zip(Brand, Name, Size, Price, Availible, Page, Link),columns=['Brand','Name','Size','Price','Availible','Page','Link'])
    ItemDF['Size'] = ItemDF['Size'].str.replace("Size:", "").str.strip()
    return ItemDF

