from config import config
from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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


#
discordbot = None
clear=""
for i in range(0,100): clear = clear + Keys.BACK_SPACE;

@log_errors
async def order(order_id):
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)
    
    data = config
    data["order"] = order["order"]
    data["user"] = order["user"]
    
    with SB(uc=True) as sb:
        driver = sb.driver
        driver.get(data["platform"]["url"])
        
        AutomatedPages = Automation(order_id=order_id,driver=driver,data=data)
        
        await AutomatedPages.hint("STAGE: initialized")

        if config["need_approval"] and not ("ideal" in config["payment_method"]):
            request_results = await AutomatedPages.request_approval()
            if request_results == "accepted":
                await AutomatedPages.hint("STAGE: Recieved approval!")
            elif request_results == "rejected":
                await AutomatedPages.hint("STAGE: Rejected ;w;")
                await AutomatedPages.hint("STAGE: Breakdown, Breakdown!")
                driver.quit()
                return
            else:
                await AutomatedPages.hint("STAGE: Timeout")
                await AutomatedPages.hint("STAGE: Breakdown, Breakdown!")
                driver.quit()
                return
        
        await AutomatedPages.combo_page()
        await AutomatedPages.main_page()
        await AutomatedPages.resturant_page()
        await AutomatedPages.login_page()
        await AutomatedPages.checkout_page()

        if "creditcard" in config["payment_method"]:
            await AutomatedPages.payment_CreditCard()
        elif "ideal" in config["payment_method"]:
            await AutomatedPages.request_approval()
            await AutomatedPages.payment_Ideal()
        else:
            print("No method found!")
            
        tracking_link = await AutomatedPages.get_tracking_mail_link()
        try:
            #discord
            if discordbot != None:
                await discordbot.send_message_via_order_id(order_id,f"Found! UWU\n tracking link: {tracking_link}, please contact API host if this link is wrong!")
        except:
            await discordbot.send_message_via_order_id(order_id,f"Unable to get tracking link, please contact API host ;w; (Timed out waiting for tracking mail)")
        
        if config["discord"]["order_compleet_timeout"] != 0:
            await asyncio.sleep(config["discord"]["order_compleet_timeout"])
        else:
            await asyncio.sleep(9999999999999999999999999999999)
            
        AutomatedPages.hint("STAGE: Breakdown, Breakdown!")
        driver.quit()
    return

async def get_resturant_menu(address:str, restaurant:str): 
    pass


# Web bot
class Automation:
    def __init__(self, order_id, driver, data):
        global discordbot
        self.order_id = order_id
        self.driver = driver
        self.data = data
        
        if discordbot != None:
            with open(f"orders/{self.order_id}.json", "r", encoding="utf-8") as f:
                order = json.load(f)
            
            self.discord_channel_id = int(order["discord"]["channel"])    

        return
    
    # Reusable stuff
    async def hint(self, msg, prefix:str="", subfix:str=""):
        if discordbot != None:
            await discordbot.send_message(self.discord_channel_id, f"{prefix}{msg}{subfix}")
        print(f"INFO: order {self.order_id} : {msg}")

    async def find_element(self, selector, timeout=12):
        try:
            element = self.driver.wait_for_element_visible(
                selector, timeout=timeout
            )

            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By

            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )

            await self.hint(prefix="-# ⤷ ", msg=f"Found and clickable: {selector}")
            
            return element

        except Exception as e:
            await self.hint(
                prefix="-# **X ",
                msg=f"Could not Find or Interact with: {selector}",
                subfix="**"
            )
            self.driver.quit()
            raise e

    def remove_cookies_banner(self):
        self.driver.execute_script("""
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
        self.driver.execute_script("""
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
    
    
    # Web page automations
    async def combo_page(self):
        await self.hint("STAGE: Combo page")
        self.remove_cookies_banner()
        
        web_general_area_searchbar = await self.find_element('input[data-qa="location-panel-search-input-address-element"]')
        web_general_area_searchbar.send_keys(str(self.data["user"]["address"]))

        web_general_area_list = await self.find_element('li[data-qa="location-panel-results-item-element"]')
        web_general_area_list.click()

    async def main_page(self):
        await self.hint("STAGE: Main page")
        self.remove_cookies_banner()
        
        web_restaurant_searchbar = await self.find_element('input[data-qa="restaurant-list-search-element"]')
        web_restaurant_searchbar.send_keys(str(self.data["order"]["restaurant"]) + Keys.ENTER)

        web_restaurant_list = await self.find_element('a:has(span[data-qa="restaurant-info-name"])')
        web_restaurant_list.click()

    async def resturant_page(self):
        await self.hint("STAGE: Resturaunt page")
        self.driver.execute_script("window.scrollBy(0, 500);")

        for i in self.data["order"]["items"]:
            await asyncio.sleep(2)
            self.remove_cookies_banner()
            
            item_name = i["name"]
            web_menu_search = await self.find_element('input[data-qa="menu-category-nav-search-element"]')
            web_menu_search.send_keys(clear + item_name)

            await asyncio.sleep(2)
            self.remove_cookies_banner()

            self.driver.click(
                f'//li[@data-item-id]'
                f'[.//span[@data-qa="item-name" and normalize-space()="{item_name}"]]'
            )
            
            for option in i["options"]:
                await asyncio.sleep(1)
                self.driver.click(
                    f'//pie-radio[@aria-checked="false"]'
                    f'[.//span['
                    f'(@data-qa="item-choices-variants-name" '
                    f'or @data-qa="item-choices-options-single-name") '
                    f'and normalize-space()="{option}"'
                    f']]'
                )
            
            #TODO Make food loop for more options like sauce
            self.driver.click('pie-button[data-qa="item-choices-action-submit"]')
            self.driver.wait_for_element_not_visible('pie-button[data-qa="item-choices-action-submit"]', timeout=20)
            await self.hint("Item added: " + str(item_name))

            await asyncio.sleep(1)
            
            #This is a promotion popup
            async def refresh_if_free_item_modal_appears():
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR,
                        '[data-qa="free-item-modal"]'
                    )
                    self.hint("WARN: Free-item modal detected! Please make sure order doesnt miss out on deals!\n-# Refreshing page...")
                    self.driver.refresh()
                    await asyncio.sleep(3)
                    return True

                except NoSuchElementException:
                    return False
            
            await refresh_if_free_item_modal_appears()

        web_checkout = await self.find_element('pie-button[data-qa="sidebar-action-checkout"]')
        web_checkout.click()

    async def login_page(self):
        await self.hint("STAGE: Login page")
        self.remove_cookies_banner()

        await self.hint("STAGE: Login page / Captcha")
        await asyncio.sleep(5)
        self.remove_cookies_banner()
        self.driver.uc_gui_click_captcha()

        await self.hint("STAGE: Login page / Mail")
        await asyncio.sleep(1)
        email_input = await self.find_element('input[type="email"][name="email"][autocomplete="email"]')
        email_input.send_keys(self.data["imap"]["email"] + Keys.ENTER)

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
        await self.hint(f"STAGE: Login page / Mail / Received Code: {code}")
        
        email_input = await self.find_element('input[name="otpCode"][placeholder="Enter your verification code"]')
        email_input.send_keys(code + Keys.ENTER)
        await asyncio.sleep(3)

    async def checkout_page(self):
        await self.hint("STAGE: Checkout page")
        self.remove_cookies_banner()

        web_checkout_personal = await self.find_element('[data-qa="personal-details-interactive"]',30)
        web_checkout_personal.click()

        self.driver.type('input[name="firstName"]', clear + self.data["user"]["name"])
        self.driver.type('input[name="lastName"]', clear + "roobot")
        self.driver.type('input[name="phoneNumber"]', clear + self.data["user"]["phone"] + Keys.ENTER)

        await asyncio.sleep(3)
        
        self.remove_cookies_banner()
        
        await asyncio.sleep(5)
        
        # web_checkout_adress = await self.find_element('[data-qa="delivery-address-description"]')
        # web_checkout_adress.click()

        # web_checkout_time = await self.find_element('[data-qa="shipping-time-title"]')
        # web_checkout_time.click()

        # web_checkout_time_asap = await self.find_element('[data-qa="radio-element"]')
        # web_checkout_time_asap.click()

        web_checkout_payment = await self.find_element('[data-qa="payment-method-interactive"]')
        web_checkout_payment.click()

        await asyncio.sleep(3)

    async def checkout_page_exit(self):
        web_checkout_payment_choose_submit = await self.find_element('pie-button[data-qa="payment-modal-action-submit"]')
        web_checkout_payment_choose_submit.click()

        await asyncio.sleep(1)
        
        web_checkout_order_and_pay = await self.find_element('pie-button[data-qa="proceed-checkout-button-action-submit-order"]')
        web_checkout_order_and_pay.click()
        
        await asyncio.sleep(1)
    
    
    # Requests
    async def request_approval(self):
        return await discordbot.send_order_request(self.order_id)
        # request = await discordbot.send_order_request(self.order_id)
        # if request == "accepted":
        #     return
        # elif request == "timeout":
        #     raise status.HTTP_408_REQUEST_TIMEOUT
        # elif request == "rejected":
        #     raise status.HTTP_402_PAYMENT_REQUIRED
        # else:  
        #     raise status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Payements
    async def payment_Ideal(self):
        await self.hint("STAGE: Ideal checkout")
        
        web_checkout_payment_choose = await self.find_element('[data-qa="payment-modal-ideal-element-element-element"]')
        web_checkout_payment_choose.click()

        await asyncio.sleep(1)
        
        await self.checkout_page_exit()

        url = ""
        while True:
            url = self.driver.get_current_url()
            if "https://pay" in url:
                break
            await asyncio.sleep(1)
        
        #Discord
        if discordbot != None:
            await discordbot.send_payment_request(self.order_id,url)
    
    async def payment_CreditCard(self):
        await self.hint("STAGE: Creditcard checkout")
        
        web_checkout_payment_choose = await self.find_element('[data-qa="payment-modal-creditcard-element-element-element"]')
        web_checkout_payment_choose.click()

        await asyncio.sleep(1)
        
        await self.checkout_page_exit()
        
        web_save_credit_card = await self.find_element('[data-qa="save_payment_toggle"]')
        web_save_credit_card.click()

        await asyncio.sleep(1)
        
        cc_name = await self.find_element('input[autocomplete="cc-name"]')
        cc_name.send_keys(clear + self.data["payment_method"]["creditcard"]["cc-name"])
        
        await asyncio.sleep(1)
        
        # Card number — inside an iframe
        await asyncio.sleep(1)
        iframe = await self.find_element('[data-cse="encryptedCardNumber"] iframe')
        self.driver.switch_to.frame(iframe)
        cc_number = await self.find_element('input[autocomplete="cc-number"]')
        cc_number.send_keys(clear + self.data["payment_method"]["creditcard"]["number"])
        self.driver.switch_to.default_content()

        # Expiry date — inside a separate iframe
        await asyncio.sleep(1)
        iframe = await self.find_element('[data-cse="encryptedExpiryDate"] iframe')
        self.driver.switch_to.frame(iframe)
        cc_expiry = await self.find_element('input[autocomplete="cc-exp"]')
        cc_expiry.send_keys(clear + self.data["payment_method"]["creditcard"]["expires"])
        self.driver.switch_to.default_content()

        # CVV — inside another iframe
        await asyncio.sleep(1)
        iframe = await self.find_element('[data-cse="encryptedSecurityCode"] iframe')
        self.driver.switch_to.frame(iframe)
        cc_cvv = await self.find_element('input[autocomplete="cc-csc"]')
        cc_cvv.send_keys(clear + self.data["payment_method"]["creditcard"]["cvv"])
        self.driver.switch_to.default_content()
        
        await asyncio.sleep(1)
        pay_button = await self.find_element('.pay-button--sticky-bottom button[data-qa="button"]', timeout=20)
        pay_button.click()
    

    async def get_tracking_mail_link(self):
        username = self.data["user"]["name"]
        email_body = wait_for_email(
            sender="no-reply@connect.thuisbezorgd.nl",
            subject=f"{username}, order confirmed",
            timeout=300,
        )["body"]

        import re
        from html import unescape

        def extract_tracking_link(html):
            html = unescape(html)
            match = re.search(
                r'https://www\.thuisbezorgd\.nl/foodtracker/[^\s"<>]+',
                html
            )
            return match.group(0).rstrip(").,") if match else None

        self.tracking_link = extract_tracking_link(email_body)
        
        return extract_tracking_link(email_body)

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