import seleniumbase as sb
from selenium.webdriver.common.keys import Keys
import time

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

data = {
    "takeaway":{
        "url":"https://www.thuisbezorgd.nl/",
    },
    "restaurant":{
        "name":"Domino's",
        "cart":[
            {
                "name":"Hot Chicken Pizza", #Exact name of the TakeAway website's element
                "options":[
                    "(25cm) Medium", #Exact name of the TakeAway website's element
                    "Classic Crust", #Exact name of the TakeAway website's element
                ]
            }
        ]
    },
    "user":{
        "name":"Roobot",
        "phonenumber":"+31655555555", #For the Delivery furry incase he cant find you
        "adress":"Oorweg 7, 1324 ZX Almere"
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
    
    for option in i["options"]:
        time.sleep(1)
        driver.click(
            f'//span['
            f'(@data-qa="item-choices-variants-name" '
            f'or @data-qa="item-choices-options-single-name") '
            f'and normalize-space()="{option}"'
            f']'
        )
    
    #TODO Make food loop for more options like sauce
    driver.click('pie-button[data-qa="item-choices-action-submit"]')

driver.click('pie-button[data-qa="sidebar-action-checkout"]')

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