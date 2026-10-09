import seleniumbase as sb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
driver.get(data["platform"]["url"])
driver.maximize_window()

clear = ""
for i in range(0,100):
    clear = clear + Keys.BACK_SPACE

def find_element(selector,timeout=12):
    driver.wait_for_element_visible(selector,timeout=timeout)
    return selector

#Combo Page
web_general_area_searchbar = find_element('input[data-qa="location-panel-search-input-address-element"]')
driver.type(web_general_area_searchbar, str(data["user"]["address"]))

web_general_area_list = find_element('li[data-qa="location-panel-results-item-element"]')
driver.click(web_general_area_list)

#Main page
web_restaurant_searchbar = find_element('input[data-qa="restaurant-list-search-element"]')
driver.type(web_restaurant_searchbar, str(data["platform"]["restaurant"]) + Keys.ENTER)

web_restaurant_list = find_element('a:has(span[data-qa="restaurant-info-name"])')
driver.click(web_restaurant_list)

#Menu resturaunt
#Remove cookies
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

for i in data["user"]["order"]:
    time.sleep(2)
    item_name = i["name"]
    web_menu_search = find_element('input[data-qa="menu-category-nav-search-element"]')
    
    #driver.type(web_menu_search, Keys.CLEAR)
    driver.type(web_menu_search, clear + item_name)
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
time.sleep(5)

driver.uc_gui_click_captcha()

time.sleep(1)

email_input = find_element('input[type="email"][name="email"][autocomplete="email"]')
driver.type(email_input, data["imap"]["email"] + Keys.ENTER)

email_body = wait_for_email(
    sender="no-reply@thuisbezorgd.nl",
    subject="Your verification code",
    timeout=300,
)["body"]

# OTP
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


code = extract_verification_code(email_body)

email_input = find_element('input[name="otpCode"][placeholder="Enter your verification code"]')
driver.type(email_input, code + Keys.ENTER)

# Checkout
time.sleep(1)

web_checkout_personal = find_element('[data-qa="personal-details-interactive"]',30)
driver.click(web_checkout_personal)

driver.type('input[name="firstName"]', clear + data["user"]["name"])
driver.type('input[name="lastName"]', clear + "roobot")
driver.type('input[name="phoneNumber"]', clear + data["user"]["phone"] + Keys.ENTER)

time.sleep(1)

# web_checkout_adress = find_element('[data-qa="delivery-address-description"]')
# driver.click(web_checkout_adress)

# web_checkout_time = find_element('[data-qa="shipping-time-title"]')
# driver.click(web_checkout_time)

# web_checkout_time_asap = find_element('[data-qa="radio-element"]')
# driver.click(web_checkout_time_asap)

# time.sleep(1)

web_checkout_payment = find_element('[data-qa="payment-method-interactive"]')
driver.click(web_checkout_payment)

time.sleep(3)

web_checkout_payment_choose = find_element('[data-qa="payment-modal-ideal-element-element-element"]')
driver.click(web_checkout_payment_choose)

time.sleep(1)

web_checkout_payment_choose_submit = find_element('pie-button[data-qa="payment-modal-action-submit"]')
driver.click(web_checkout_payment_choose_submit)

time.sleep(1)

web_checkout_order_and_pay = find_element('pie-button[data-qa="proceed-checkout-button-action-submit-order"]')
driver.click(web_checkout_order_and_pay)

elements = driver.wait_for_element("xpath", "//*[contains(., 'iDEAL')]")

url = ""
while True:
    url = driver.get_current_url()
    if "https://pay" in url:
        break
    time.sleep(1)

print(url)

time.sleep(1000)


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