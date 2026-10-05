import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

data = {
    "takeaway":{
        "url":"https://www.thuisbezorgd.nl/"
    },
    "user":{
        "name":"Windhseim",
        "city":"Almere",
        "adress":"Stadhuisstraat 18"
    }
}

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
     get: () => undefined
    })
  """
})

#driver.delete_all_cookies()

driver.get(data["takeaway"]["url"])

def find_element(method,value):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((method, value))
    )
    element = driver.find_element(method, value)
    element.clear()

    return element

web_general_area_searchbar = find_element(By.CLASS_NAME,"VO0jE")
web_general_area_searchbar.click()
web_general_area_searchbar.send_keys(f"{data["user"]["city"]}" + Keys.ENTER)

time.sleep(10)

web_general_area_button = driver.find_element(By.LINK_TEXT,f"{data["user"]["city"]}")


driver.quit()