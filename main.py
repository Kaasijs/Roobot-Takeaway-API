import seleniumbase as sb
from selenium.webdriver.common.keys import Keys
import time
from mail import wait_for_email
import json
import pprint

# -----------------------------------------------------------------------------------
#
# ██████╗░░█████╗░░█████╗░██████╗░░█████╗░████████╗  ███████╗░█████╗░░█████╗░██████╗░
# ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝  ██╔════╝██╔══██╗██╔══██╗██╔══██╗ 
# ██████╔╝██║░░██║██║░░██║██████╦╝██║░░██║░░░██║░░░  █████╗░░██║░░██║██║░░██║██║░░██║ 
# ██╔══██╗██║░░██║██║░░██║██╔══██╗██║░░██║░░░██║░░░  ██╔══╝░░██║░░██║██║░░██║██║░░██║ 
# ██║░░██║╚█████╔╝╚█████╔╝██████╦╝╚█████╔╝░░░██║░░░  ██║░░░░░╚█████╔╝╚█████╔╝██████╔╝ 
# ╚═╝░░╚═╝░╚════╝░░╚════╝░╚═════╝░░╚════╝░░░░╚═╝░░░  ╚═╝░░░░░░╚════╝░░╚════╝░╚═════╝░ 
#
#                        By Kaasijs, https://kaasijs.github.io/
#
#             A Dockerized bot for ordering food of just eat takeaway websites
#                                   With json input
#
# --------------------------------  Python Librarys  --------------------------------
#
#                               pip install seleniumbase
#
# -----------------------------------------------------------------------------------

with open('data.json', 'r') as f:
    data = json.load(f)
pprint.pp(data)

driver = sb.Driver(uc=True)
driver.get(data["takeaway"]["url"])
driver.maximize_window()
    
def find_element(selector):
    driver.wait_for_element_visible(selector)
    return selector

#Combo Page
web_general_area_searchbar = find_element('input[data-qa="location-panel-search-input-address-element"]')
driver.type(web_general_area_searchbar, str(data["user"]["adress"]))

web_general_area_list = find_element('li[data-qa="location-panel-results-item-element"]')
driver.click(web_general_area_list)

#Main page
web_restaurant_searchbar = find_element('input[data-qa="restaurant-list-search-element"]')
driver.type(web_restaurant_searchbar, str(data["restaurant"]["name"]) + Keys.ENTER)

web_restaurant_list = find_element('a:has(span[data-qa="restaurant-info-name"])')
driver.click(web_restaurant_list)

#Menu resturaunt
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
    web_menu_search = find_element('input[data-qa="menu-category-nav-search-element"]')
    
    driver.type(web_menu_search, item_name)
    print(item_name + Keys.ENTER)

    time.sleep(2)

    driver.click(
        f'//li[@data-item-id]'
        f'[.//span[@data-qa="item-name" and normalize-space()="{item_name}"]]'
    )
    
    for option in i["options"]:
        time.sleep(1)
        driver.click(
            f'//span['
            f'(@data-qa="item-choices-variants-name" '
            f'or @data-qa="item-choices-options-single-name")'
            f'and normalize-space()="{option}"'
            f']'
        )
    
    #TODO Make food loop for more options like sauce
    web_add_to_cart = find_element('pie-button[data-qa="item-choices-action-submit"]')
    driver.click('pie-button[data-qa="item-choices-action-submit"]')
    driver.wait_for_element_not_visible('pie-button[data-qa="item-choices-action-submit"]', timeout=20)

web_checkout = find_element('pie-button[data-qa="sidebar-action-checkout"]')
driver.click(web_checkout)

#Login

#Cloudflare captcha
time.sleep(8)

driver.uc_gui_click_captcha()

time.sleep(1)

email_input = find_element('input[type="email"][name="email"][autocomplete="email"]')
driver.type(email_input, data["user"]["email"] + Keys.ENTER)

email_body = wait_for_email(
    sender="no-reply@thuisbezorgd.nl",
    subject="Your verification code",
    timeout=300
)["body"]

import re
from bs4 import BeautifulSoup

def extract_verification_code(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the text inside the email's code box
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)

        if re.fullmatch(r"[A-Z0-9]{6}", text):
            return text

    return None


# Example
code = extract_verification_code(email_body)

email_input = find_element('form[data-qa="otp-page-form"]')
driver.type(email_input, data["user"]["email"] + Keys.ENTER)

time.sleep(10000)

driver.quit()

# ⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⢗⡺⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠈⠗⠉⡄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠘⢤⢜⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⣇⢃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⣀⣑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠹⡌⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠐⢄⠀⠀⠀⡠⢄⡀⠸⢠⠁⠀⢢⠙⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⢓⡔⣌⡄⠀⠀⠀⠀⠀⠀⠀⡆⠐⠆⠑⢄⣐⡀⠀⠀⠁⠀⠠⡀⠀⢃⠀⢃⠀⠀⠀⠀⡀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⢜⡘⣴⡄⠀⠀⠀⠀⠀⠀⠇⡆⠘⡦⠉⠀⠀⠀⢀⠤⡀⠀⠈⠢⠘⠀⢸⠀⠀⠠⠊⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠈⠳⠧⠍⡄⠀⠀⠀⠀⠀⡆⠁⠀⡇⠀⣒⠄⠀⠈⢀⠵⣒⣤⣀⠀⠀⢘⡀⠀⠁⠤⠄⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⢣⠀⠸⡜⠄⠀⠀⠀⠀⢃⠘⡤⠇⢀⢴⣄⠀⠀⠏⠀⢿⣸⣿⡂⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠈⠄⠠⠰⡳⡀⠀⠀⠀⠈⢂⠀⠀⡏⠸⣝⡄⡀⠀⠀⠀⠉⠀⡤⠄⠐⡆⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⢃⢃⠀⠀⠀⠀⠈⢢⠐⠇⠀⠛⠵⠃⠀⢀⠆⠀⠀⠃⢀⠐⡇⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠤⠡⣼⡊⠆⠀⠀⠀⠀⠀⠰⠀⠚⠁⠀⠔⠉⠁⠀⠀⢠⣔⢉⠴⠁⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠘⣀⣋⠟⡜⡀⠀⠀⠀⠀⠐⠦⣤⣤⢄⠀⠀⠀⠀⠀⠀⠸⡳⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⣀⠔⢡⠚⡏⢰⢡⠀⠀⠀⠀⠀⠀⠤⠚⢵⠖⠉⠉⠉⠀⣄⠄⠁⠀⢈⡣⢄⡀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠋⠉⠒⠊⠁⠀⡹⡄⢃⢃⠀⢀⠤⡂⢹⢀⠔⠉⠶⣿⡿⠷⠀⠘⢄⠀⡰⢀⠀⢁⠊⢑⡄⠀⠀⠀
# ⠀⠀⠀⠀⢸⢀⠀⠀⢀⢠⡞⣮⡘⡄⠘⣤⠞⡅⠀⢈⠁⠀⠀⢁⠀⣀⠈⠀⠀⠀⢹⠁⠀⡝⠁⠀⠀⠣⡀⠀⠀
# ⠀⠀⠀⠀⠈⠉⠈⠉⠀⢀⢗⣙⠟⢡⡟⣼⠀⣻⠀⡘⣎⠭⠴⠤⠼⠤⠤⠧⠹⡱⢊⠀⡜⠀⠀⠀⠀⠀⡌⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⠐⠂⢠⡕⢰⡷⠇⠘⡷⢑⣪⣉⠹⠉⠠⠉⠏⣹⣁⡒⠸⣸⠀⠀⠀⠀⠀⠀⠓⡄⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡌⠈⣬⠃⣸⠐⢄⠠⠇⠐⢫⠙⠛⠛⡍⢉⠉⠒⠒⠂⢤⡷⡤⠄⠀⠀⡄⠒⠚⠲⡆
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⡭⠄⡰⢻⠀⠘⡶⣀⣀⢸⢆⣀⡠⣿⠹⣤⣀⣀⣀⣰⢿⠋⠀⠂⠀⣃⡀⠄⠒⣇
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡐⠐⢁⠆⠀⠀⢡⠔⠣⢬⠠⠀⣄⠌⠰⢌⡠⠤⠭⢀⢩⠃⠀⠀⠀⡄⠀⠀⠀⡆
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡧⠤⠊⠀⠀⠀⡌⠀⠁⡏⠈⠁⠋⠈⠉⢸⠁⠉⠁⢃⠉⣇⠀⠀⠠⠇⠀⠀⠀⡡
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢃⠀⠀⠀⠀⢀⠗⠒⠐⠑⠒⢢⠤⠠⠤⢸⠐⠂⠤⠼⠀⣟⠀⠀⠀⠐⠒⠒⠊⣱