import asyncio
import discordbot
import json
import traceback
from mail import wait_for_email

with open('config.json', 'r') as f:
    config = json.load(f)

if "creditcard" in config["payment_method"]:
    print("creditcard")

elif "ideal" in config["payment_method"]:
    print("ideal")
    
else:
    print("No method found!")

# email_body = wait_for_email(
#     sender="nekorooni@gmail.com",
#     subject="Fwd: Jeroen, order confirmed",
#     timeout=300,
#     inbox="Inbox",
# )["body"]

# import re
# from html import unescape

# def extract_tracking_link(html):
#     html = unescape(html)
#     match = re.search(
#         r'https://www\.thuisbezorgd\.nl/foodtracker/[^\s"<>]+',
#         html
#     )
#     return match.group(0).rstrip(").,") if match else None

# print(extract_tracking_link(email_body))





# async def main():
#     async with discordbot.client:
#         await discordbot.client.start(config["discord"]["token"])

# @discordbot.client.event
# async def on_ready():
#     print("ready")
#     order_id = "0c4f2946"
    
#     await discordbot.create_order(order_id)
    
#     request = await discordbot.send_order_request(order_id)
#     if request == "accepted":
        
#         await discordbot.send_payment_request(order_id,"https://kaasijs.com")
    
#     else:  
#         await discordbot.client.close()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main(), debug=True)
#     except Exception:
#         traceback.print_exc()