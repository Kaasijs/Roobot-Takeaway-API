from config import config
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

        await AutomatedPages.combo_page()
        await AutomatedPages.main_page()
        await AutomatedPages.resturant_page()
        await AutomatedPages.login_page()
        await AutomatedPages.checkout_page()
        if config["need_approval"]:
            await AutomatedPages.request_approval()

        if "creditcard" in config["payment_method"]:
            await AutomatedPages.payment_CreditCard()
        elif "ideal" in config["payment_method"]:
            await AutomatedPages.payment_Ideal()
        else:
            print("No method found!")
            
        tracking_link = await AutomatedPages.get_tracking_mail_link()
        try:
            #discord
            if discordbot != None:
                await discordbot.send_message(order_id,f"Sucess! UWU\n tracking link: {tracking_link}")
        except:
            await discordbot.send_message(order_id,f"Unable to get tracking link, please contact API host ;w;")
        
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
            self.driver.wait_for_element_visible(selector, timeout=timeout)
            #self.driver.wait_for_element_clickable(selector, timeout=timeout)

        except Exception as e:
            await self.hint(prefix="-# **X ", msg=f"Could not Find or Interact with: {selector}", subfix="**")
            self.driver.quit()
            raise e

        await self.hint(prefix="-# ⤷ ", msg=f"Found and clickable: {selector}")

        return selector

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
        self.driver.type(web_general_area_searchbar, str(self.data["user"]["address"]))

        web_general_area_list = await self.find_element('li[data-qa="location-panel-results-item-element"]')
        self.driver.click(web_general_area_list)

    async def main_page(self):
        await self.hint("STAGE: Main page")
        self.remove_cookies_banner()
        
        web_restaurant_searchbar = await self.find_element('input[data-qa="restaurant-list-search-element"]')
        self.driver.type(web_restaurant_searchbar, str(self.data["order"]["restaurant"]) + Keys.ENTER)

        web_restaurant_list = await self.find_element('a:has(span[data-qa="restaurant-info-name"])')
        self.driver.click(web_restaurant_list)

    async def resturant_page(self):
        await self.hint("STAGE: Resturaunt page")
        self.driver.execute_script("window.scrollBy(0, 500);")

        for i in self.data["order"]["items"]:
            await asyncio.sleep(2)
            self.remove_cookies_banner()
            
            item_name = i["name"]
            web_menu_search = await self.find_element('input[data-qa="menu-category-nav-search-element"]')
            
            self.driver.type(web_menu_search, clear + item_name)

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

        web_checkout = await self.find_element('pie-button[data-qa="sidebar-action-checkout"]')
        self.driver.click(web_checkout)

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
        self.driver.type(email_input, self.data["imap"]["email"] + Keys.ENTER)

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
        self.driver.type(email_input, code + Keys.ENTER)
        await asyncio.sleep(3)

    async def checkout_page(self):
        await self.hint("STAGE: Checkout page")
        self.remove_cookies_banner()

        web_checkout_personal = await self.find_element('[data-qa="personal-details-interactive"]',30)
        self.driver.click(web_checkout_personal)

        self.driver.type('input[name="firstName"]', clear + self.data["user"]["name"])
        self.driver.type('input[name="lastName"]', clear + "roobot")
        self.driver.type('input[name="phoneNumber"]', clear + self.data["user"]["phone"] + Keys.ENTER)

        await asyncio.sleep(3)
        
        self.remove_cookies_banner()
        
        await asyncio.sleep(3)
        
        # web_checkout_adress = await self.find_element('[data-qa="delivery-address-description"]')
        # self.driver.click(web_checkout_adress)

        # web_checkout_time = await self.find_element('[data-qa="shipping-time-title"]')
        # self.driver.click(web_checkout_time)

        # web_checkout_time_asap = await self.find_element('[data-qa="radio-element"]')
        # self.driver.click(web_checkout_time_asap)

        web_checkout_payment = await self.find_element('[data-qa="payment-method-interactive"]')
        self.driver.click(web_checkout_payment)

        await asyncio.sleep(3)

    async def checkout_page_exit(self):
        web_checkout_payment_choose_submit = await self.find_element('pie-button[data-qa="payment-modal-action-submit"]')
        self.driver.click(web_checkout_payment_choose_submit)

        await asyncio.sleep(1)
        
        web_checkout_order_and_pay = await self.find_element('pie-button[data-qa="proceed-checkout-button-action-submit-order"]')
        self.driver.click(web_checkout_order_and_pay)
        
        await asyncio.sleep(1)
    
    
    # Requests
    async def request_approval(self):
        request = await discordbot.send_order_request(self.order_id)
        if request == "accepted":
            return
        elif request == "timeout":
            raise status.HTTP_408_REQUEST_TIMEOUT
        elif request == "rejected":
            raise status.HTTP_402_PAYMENT_REQUIRED
        else:  
            raise status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Payements
    async def payment_Ideal(self):
        await self.hint("STAGE: Ideal checkout")
        
        web_checkout_payment_choose = await self.find_element('[data-qa="payment-modal-ideal-element-element-element"]')
        self.driver.click(web_checkout_payment_choose)

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
        self.driver.click(web_checkout_payment_choose)

        await asyncio.sleep(1)
        
        await self.checkout_page_exit()
        
        web_save_credit_card = await self.find_element('[data-qa="save_payment_toggle"]')
        self.driver.click(web_save_credit_card)

        await asyncio.sleep(1)
        
        cc_name = await self.find_element('input[autocomplete="cc-name"]')
        self.driver.type(cc_name, clear + self.data["payment_method"]["creditcard"]["cc-name"])
        
        await asyncio.sleep(1)
        
        cc_name = await self.find_element('input[data-fieldtype="encryptedCardNumber"]')
        self.driver.type(cc_name, clear + self.data["payment_method"]["creditcard"]["number"])
        
        await asyncio.sleep(1)
        
        cc_name = await self.find_element('input[data-fieldtype="encryptedExpiryDate"]')
        self.driver.type(cc_name, clear + self.data["payment_method"]["creditcard"]["expires"])
        
        await asyncio.sleep(1)
        
        cc_name = await self.find_element('input[data-fieldtype="encryptedSecurityCode"]')
        self.driver.type(cc_name, clear + self.data["payment_method"]["creditcard"]["cvv"])
        
        await asyncio.sleep(1)
        
        pay_button = await self.find_element('[data-qa="button"]',timeout=20)
        #self.driver.click(pay_button)
    

    async def get_tracking_mail_link(self):
        username = self.data["user"]["name"]
        email_body = wait_for_email(
            sender="no-reply@connect.thuisbezorgd.nl",
            subject=f"{username}, order confirmed",
            timeout=300,
            inbox="Inbox",
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