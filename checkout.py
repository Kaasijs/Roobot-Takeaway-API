import seleniumbase as sb
from selenium.webdriver.common.keys import Keys
import time
from mail import wait_for_email
import json
import pprint

with open('data.json', 'r') as f:
    data = json.load(f)
pprint.pp(data)

driver = sb.Driver(uc=True)
driver.get("file:///C:/Users/vandu/Downloads/Food%20Delivery,%20Groceries%20&%20More%20Near%20You%20_%20Thuisbezorgd.nl.html")
driver.maximize_window()
    
def find_element(selector):
    driver.wait_for_element_visible(selector)
    return selector

web_checkout_personal = '[data-qa="personal-details-interactive"]'
driver.remove_element(web_checkout_personal)
