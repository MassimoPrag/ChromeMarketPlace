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


def scrapeYP():
    #base_url = "https://ypcollective.com"
    base = "https://ypcollective.com/collections/chrome-hearts"

    driver = webdriver.Chrome(options=options)

    #establish lists
    Brand, Name, Size, Price, Available, Page, Link = [], [], [], [], [], [], []

    for i in range(1, 6):
        pgURL = f"{base}?page={i}"
        driver.get(pgURL)
        time.sleep(5)

        listings = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="product-grid"]//li[contains(@class, "grid__item")]'))
        )

        for listing in listings:
            name = listing.find_element(By.XPATH, './/a[@class="full-unstyled-link"]').text.strip()
            Name.append(name)

            try:
                price = listing.find_element(By.XPATH, ".//span[@class='price-item price-item--regular']").text.strip()
            except NoSuchElementException:
                price = "N/A"
            Price.append(price)

            link_element = listing.find_element(By.XPATH, ".//a[@class='full-unstyled-link']")
            linkHref = link_element.get_dom_attribute("href")
            linkHref = f"https://ypcollective.com{linkHref}"
            Link.append(linkHref)

            brand = "Chrome Hearts"
            Brand.append(brand)
            try:
                size = listing.find_element(By.XPATH, ".//h4[contains(text(), 'Size:')]").text.strip()
                size = size.split('\n')[0]
            except NoSuchElementException:
                size = "N/A"
            Size.append(size)
            Page.append(i)
            Available.append(True)

    driver.quit()
    ItemDF = pd.DataFrame(zip(Brand, Name, Size, Price, Available, Page, Link), columns=['Brand', 'Name', 'Size', 'Price', 'Availible', 'Page', 'Link'])
    return ItemDF


def main():
    x = x

if __name__ == "__main__":
    main()




#click on next arrow for last number - 1 times showed in the page list