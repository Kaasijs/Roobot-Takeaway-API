import pprint
import seleniumbase as sb
#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options  import Options
#from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
import time

data = {
    "takeaway":{
        "url":"https://www.thuisbezorgd.nl/",
    },
    "restaurant":{
        "name":"KFC",
        "cart":[{
            "name":"Bucket 15 Filet Bites",
            "options":""
            }]
    },
    "user":{
        "name":"Windhseim",
        "city":"Amsterdam",
        "adress":"Torontoweg 101, 1334 KT Almere"
    }
}

driver = sb.Driver(uc=True)
driver.get(data["takeaway"]["url"])
driver.maximize_window()
    
def find_element(selector):
    driver.wait_for_element_visible(selector)
    return selector

web_general_area_searchbar = find_element('input[data-qa="location-panel-search-input-address-element"]')
driver.type(web_general_area_searchbar, str(data["user"]["adress"]))

web_general_area_list = find_element('li[data-qa="location-panel-results-item-element"]')
driver.click(web_general_area_list)

web_restaurant_searchbar = find_element('input[data-qa="restaurant-list-search-element"]')
driver.type(web_restaurant_searchbar, str(data["restaurant"]["name"]) + Keys.ENTER)

web_restaurant_list = find_element('a:has(span[data-qa="restaurant-info-name"])')
driver.click(web_restaurant_list)

driver.execute_script("""
    const style = document.createElement("style");
    style.textContent = `
        pie-cookie-banner {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
    `;
    document.head.appendChild(style);
""")

driver.execute_script("window.scrollBy(0, 500);")

for i in data["restaurant"]["cart"]:
    time.sleep(1)
    item_name = i["name"]
    menu_search = 'input[data-qa="menu-category-nav-search-element"]'
    
    driver.type(menu_search, item_name)
    print(item_name + Keys.ENTER)

    time.sleep(2)

    driver.click(
        f'//li[@data-item-id]'
        f'[.//span[@data-qa="item-name" and normalize-space()="{item_name}"]]'
    )
    
    #TODO Make food loop for more options like sauce
    driver.click('pie-button[data-qa="item-choices-action-submit"]')

driver.click('pie-button[data-qa="sidebar-action-checkout"]')

time.sleep(1000)

driver.quit()