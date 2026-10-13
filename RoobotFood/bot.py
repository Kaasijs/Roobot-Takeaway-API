from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
import asyncio
from mail import wait_for_email
import json
import traceback
from functools import wraps
import re
from bs4 import BeautifulSoup
from fastapi import status

def log_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise

    return wrapper

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

@log_errors
async def order(order_id, discordbot=None):
    # load order
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)
    
    data = config
    data["order"] = order["order"]
    data["user"] = order["user"]
    
    clear=""
    for i in range(0,100): clear = clear + Keys.BACK_SPACE;
    
    discord_channel_id=None
    if discordbot != None:
        discord_channel_id = int(order["discord"]["channel"])
    
    async def hint(msg, prefix:str="", subfix:str=""):
        if discordbot != None:
            await discordbot.send_message(discord_channel_id, f"{prefix}{msg}{subfix}")
        print(f"INFO: order {order_id} : {msg}")
        
    
    with SB(uc=True) as sb:
        driver = sb.driver
        
        driver.get(data["platform"]["url"])
        
        await hint("STAGE: initialized")
        
        async def find_element(selector,timeout=12):
            try:
                driver.wait_for_element_visible(selector,timeout=timeout)
            except Exception:
                await hint(prefix="-# **X ", msg=f"Could not Find or Interact with: {selector}", subfix="**")
                driver.quit()
                raise Exception
            finally:
                await hint(prefix="-# ⤷ ", msg=f"Found: {selector}")
                return selector

        def remove_cookies_banner():
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
            driver.execute_script("""
                function hideCookieBanner() {
                    document.querySelectorAll('pie-cookie-banner').forEach(banner => {
                        banner.style.setProperty('display', 'none', 'important');
                    });
                }

                hideCookieBanner();

                new MutationObserver(hideCookieBanner).observe(
                    document.documentElement,
                    { childList: true, subtree: true }
                );
            """)
        
        async def combo_page():
            await hint("STAGE: Combo page")
            remove_cookies_banner()
            
            web_general_area_searchbar = await find_element('input[data-qa="location-panel-search-input-address-element"]')
            driver.type(web_general_area_searchbar, str(data["user"]["address"]))

            web_general_area_list = await find_element('li[data-qa="location-panel-results-item-element"]')
            driver.click(web_general_area_list)

        async def main_page():
            await hint("STAGE: Main page")
            remove_cookies_banner()
            
            web_restaurant_searchbar = await find_element('input[data-qa="restaurant-list-search-element"]')
            driver.type(web_restaurant_searchbar, str(data["order"]["restaurant"]) + Keys.ENTER)

            web_restaurant_list = await find_element('a:has(span[data-qa="restaurant-info-name"])')
            driver.click(web_restaurant_list)
        
        async def resturant_page():
            await hint("STAGE: Resturaunt page")
            driver.execute_script("window.scrollBy(0, 500);")

            for i in data["order"]["items"]:
                await asyncio.sleep(2)
                remove_cookies_banner()
                
                item_name = i["name"]
                web_menu_search = await find_element('input[data-qa="menu-category-nav-search-element"]')
                
                driver.type(web_menu_search, clear + item_name)

                await asyncio.sleep(2)
                remove_cookies_banner()

                driver.click(
                    f'//li[@data-item-id]'
                    f'[.//span[@data-qa="item-name" and normalize-space()="{item_name}"]]'
                )
                
                for option in i["options"]:
                    await asyncio.sleep(1)
                    driver.click(
                        f'//span['
                        f'(@data-qa="item-choices-variants-name" '
                        f'or @data-qa="item-choices-options-single-name")'
                        f'and normalize-space()="{option}"'
                        f']'
                    )
                
                #TODO Make food loop for more options like sauce
                driver.click('pie-button[data-qa="item-choices-action-submit"]')
                driver.wait_for_element_not_visible('pie-button[data-qa="item-choices-action-submit"]', timeout=20)
                await hint("Item added: " + str(item_name))

            web_checkout = await find_element('pie-button[data-qa="sidebar-action-checkout"]')
            driver.click(web_checkout)

        async def login_page():
            await hint("STAGE: Login page")
            remove_cookies_banner()

            await hint("STAGE: Login page / Captcha")
            await asyncio.sleep(5)
            remove_cookies_banner()
            driver.uc_gui_click_captcha()

            await hint("STAGE: Login page / Mail")
            await asyncio.sleep(1)
            email_input = await find_element('input[type="email"][name="email"][autocomplete="email"]')
            driver.type(email_input, data["imap"]["email"] + Keys.ENTER)

            email_body = wait_for_email(
                sender="no-reply@thuisbezorgd.nl",
                subject="Your verification code",
                timeout=300,
            )["body"]

            def extract_verification_code(html):
                soup = BeautifulSoup(html, "html.parser")
                # Find the text inside the email's code box
                for td in soup.find_all("td"):
                    text = td.get_text(strip=True)
                    if re.fullmatch(r"[A-Z0-9]{6}", text):
                        return text
                return None

            code = extract_verification_code(email_body)
            await hint(f"STAGE: Login page / Mail / Received Code: {code}")
            
            email_input = await find_element('input[name="otpCode"][placeholder="Enter your verification code"]')
            driver.type(email_input, code + Keys.ENTER)
            await asyncio.sleep(3)

        async def checkout_page():
            await hint("STAGE: Checkout page")
            remove_cookies_banner()

            web_checkout_personal = await find_element('[data-qa="personal-details-interactive"]',30)
            driver.click(web_checkout_personal)

            driver.type('input[name="firstName"]', clear + data["user"]["name"])
            driver.type('input[name="lastName"]', clear + "roobot")
            driver.type('input[name="phoneNumber"]', clear + data["user"]["phone"] + Keys.ENTER)

            await asyncio.sleep(1)
            
            remove_cookies_banner()

            # web_checkout_adress = await find_element('[data-qa="delivery-address-description"]')
            # driver.click(web_checkout_adress)

            # web_checkout_time = await find_element('[data-qa="shipping-time-title"]')
            # driver.click(web_checkout_time)

            # web_checkout_time_asap = await find_element('[data-qa="radio-element"]')
            # driver.click(web_checkout_time_asap)

            # await asyncio.sleep(1)

            web_checkout_payment = await find_element('[data-qa="payment-method-interactive"]')
            driver.click(web_checkout_payment)

            await asyncio.sleep(3)

            web_checkout_payment_choose = await find_element('[data-qa="payment-modal-ideal-element-element-element"]')
            driver.click(web_checkout_payment_choose)

            await asyncio.sleep(1)

            web_checkout_payment_choose_submit = await find_element('pie-button[data-qa="payment-modal-action-submit"]')
            driver.click(web_checkout_payment_choose_submit)

            await asyncio.sleep(1)
        
        async def request_approval():
            request = await discordbot.send_order_request(order_id)
            if request == "accepted":
                await request_payment()
            if request == "timeout":
                raise status.HTTP_408_REQUEST_TIMEOUT
            if request == "rejected":
                raise status.HTTP_402_PAYMENT_REQUIRED
            else:  
                raise status.HTTP_500_INTERNAL_SERVER_ERROR
        
        async def request_payment():
            await hint("STAGE: Ideal checkout")
            web_checkout_order_and_pay = await find_element('pie-button[data-qa="proceed-checkout-button-action-submit-order"]')
            driver.click(web_checkout_order_and_pay)

            #elements = driver.wait_for_element("xpath", "//*[contains(., 'iDEAL')]")
            url = ""
            while True:
                url = driver.get_current_url()
                if "https://pay" in url:
                    break
                await asyncio.sleep(1)
            
            await discordbot.send_payment_request(order_id,url)
                
        await combo_page()
        await main_page()
        await resturant_page()
        await login_page()
        await checkout_page()
        await request_approval()
        
        await hint("STAGE: Breakdown, Breakdown!")
        driver.quit()
    return

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