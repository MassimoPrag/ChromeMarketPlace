"""
Scrape Archive threads
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


# https://www.archivethreads.ca/search-results?q=chrome+hearts&type=products&page=2&collections=Chrome+Hearts
def scrapeArchive():
    base = "https://www.archivethreads.ca/search-results?q=chrome+hearts&type=products&collections=Chrome+Hearts"
    Name, Price, Available, Time, Page, Link = [], [], [], [], [], []
    driver = webdriver.Chrome(options=options)
    for page in range(1,2):
        pageURL = f"https://www.archivethreads.ca/search-results?q=chrome+hearts&type=products&page={page}&collections=Chrome+Hearts"
        driver.get(pageURL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='DS54bMt']/li[@data-hook='grid-layout-item']")))


        listings = driver.find_elements(By.XPATH, "//li[@data-hook='grid-layout-item']")#"//li[@data-hook='grid-layout-item']" //ul[@class='DS54bMt']/li[@data-hook='grid-layout-item']

        print(f"Number of listings found on page {page}: {len(listings)}")

      



        for listing in listings:
            name = listing.find_element(By.XPATH, ".//a[@data-hook='item-title']").text
            price = listing.find_element(By.XPATH, ".//span[@data-hook='item-price']").text
            t = "N/A"
            link = listing.find_element(By.XPATH, ".//a[@data-hook='item-title']").get_dom_attribute("href")
            
            #availible
            check_add_to_cart = listing.find_element(By.XPATH, "//button[@data-hook='add-to-cart-button']")
            aria_disabled = check_add_to_cart.get_dom_attribute("aria-disabled")
            available = aria_disabled != "true"
           
            

            Name.append(name)
            Price.append(price)
            Time.append(t)
            Available.append(available)
            Page.append(page)
            Link.append(link)

    driver.quit()
    ItemDF=pd.DataFrame(zip(Name, Price, Available, Time, Page, Link),columns=['Name','Price','Available','Time','Page','Link'])
    
    Size = []
    for links in ItemDF['Link']:
        driver.get(links)
        time.sleep(5)
        try:
            size = driver.find_element(By.XPATH, ".//div[@data-hook='dropdown-option']//span[@class='sMgpOzd o_waQ4x---typography-11-runningText o_waQ4x---priority-7-primary sdv4_87' and @aria-hidden='false']").text
        except:
            size = "N/A"
        Size.append(size)
    ItemDF['Size'] = Size
    
      
    
    
    return ItemDF




"""link_ele = driver.find_element(By.XPATH,".//a[@data-hook='item-title']")# need to click into each element
            link_ele.click()
            time.sleep(5)
            try:
                size = driver.find_element(By.XPATH, ".//div[@data-hook='dropdown-option']//span[@class='sMgpOzd o_waQ4x---typography-11-runningText o_waQ4x---priority-7-primary sdv4_87' and @aria-hidden='false']").text
            except:
                size = "N/A"
    """

print(scrapeArchive())
    





