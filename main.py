import pprint
from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

data = {
    "takeaway":{
        "url":"https://www.thuisbezorgd.nl/",
    },
    "restaurant":{
        "name":"KFC",
        "food":["Filet bites"]
    },
    "user":{
        "name":"Windhseim",
        "city":"Amsterdam",
        "adress":"Stadhuisstraat 18"
    }
}

driver = Driver(uc=True)
driver.get(data["takeaway"]["url"])
driver.maximize_window()
time.sleep(2)
    
def find_element(method,value):    
    WebDriverWait(driver, 4).until(
        EC.presence_of_element_located((method, value))
    )
    element = driver.find_element(method, value)

    return element

#web_general_area_searchbar = find_element(By.ID,"combobox-input_0")
web_general_area_searchbar = find_element(By.CSS_SELECTOR, 'input[data-qa="location-panel-search-input-address-element"]')
web_general_area_searchbar.send_keys(str(data["user"]["adress"]))

time.sleep(3)

web_general_area_list = find_element(By.CSS_SELECTOR, 'li[data-qa="location-panel-results-item-element"]')
web_general_area_list.click()

time.sleep(3)

web_restaurant_searchbar = find_element(By.CSS_SELECTOR, 'input[data-qa="restaurant-list-search-element"]')
web_restaurant_searchbar.send_keys(str(data["restaurant"]["name"]) + Keys.ENTER)

time.sleep(3)

web_restaurant_list = find_element(By.CSS_SELECTOR, 'a:has(span[data-qa="restaurant-info-name"])')
web_restaurant_list.click()

time.sleep(3)

#TODO Make food loop for more items
web_restaurant_menu_searchbar = find_element(By.CSS_SELECTOR, 'input[data-qa="menu-category-nav-search-element"]')
web_restaurant_searchbar.send_keys(str(data["restaurant"]["food"][0]) + Keys.ENTER)

time.sleep(3)

driver.execute_script("window.scrollBy(0, 500);")
web_restaurant_list = find_element(By.CSS_SELECTOR, 'button[data-test-id="pie-icon-button"]')
web_restaurant_list.click()

time.sleep(3)


time.sleep(1000)

driver.quit()