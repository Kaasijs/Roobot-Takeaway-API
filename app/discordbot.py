from config import config
import discord
from discord.ext import commands
from urllib.request import Request, urlopen
import json
import traceback
import asyncio
from functools import wraps
from models import *
import bot

category_id = int(config["discord"]["category_id"])

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)


# Error handeling
def log_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise

    return wrapper

@log_errors
@client.event
async def on_error(event, *args, **kwargs):
    import traceback
    traceback.print_exc()


# Ready
@log_errors
@client.event
async def on_ready():
    GUILD_ID = int(config["discord"]["guild_id"])
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
    else:
        await client.tree.sync()
    print(f"Discord: Ready as {client.user}!")


#commands
disclaimer:str = "| By using this command you agree with info being shared with delivery and just eat take-a-way services, and temporarly saved on server host!"

@client.tree.command(name="user", description=f"Update your FoodAPI infromation")
@discord.app_commands.describe(
    address=f"Example format: Torontoweg 101, 1334 KT Almere {disclaimer}",
    phone=f"Example format: +31655555555 {disclaimer}",
    )
@log_errors
async def user(interaction: discord.Interaction, address:str, phone:str):
    payload = User(
            name=str(interaction.user),
            address=address,
            phone=phone
        )
    
    with open(f"users/{interaction.user.id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(payload.model_dump(), indent=4))

    await interaction.response.send_message(f"User updated!",ephemeral=True)

## TODO ORDERING. DISPLAY MENU. POST REQUEST TO ITSELF WHEN DONE  
# @client.tree.command(name="order_create", description="Order something!")
# @discord.app_commands.describe(
#     restaurant=f"Example format: KFC {disclaimer}",
#     )
# @log_errors
# async def order_create(interaction: discord.Interaction, restaurant:str):
#     await interaction.response.send_message(f"Checking restaurant in your area matching that {restaurant}",ephemeral=True)
    
#     if not Path(f"users/{interaction.user.id}.json").exists():
#         await interaction.response.send_message(f"Please use /user first",ephemeral=True)
#         return
    
#     with open(f"users/{interaction.user.id}.json", "r", encoding="utf-8") as f:
#         user = json.load(f)
    
#     menu:list = await bot.get_resturant_menu(address=user.address, restaurant=restaurant)
    
#     payload = Order(
#             restaurant=restaurant
#         )

    
#     with open(f"users/{interaction.user.id}.json", "w", encoding="utf-8") as f:
#         f.write(json.dumps(payload.model_dump(), indent=4))
    
#     await interaction.response.send_message(f"User updated!",ephemeral=True)

    # request = Request(
    #     "127.0.0.1:8000",
    #     data=json.dumps(payload).encode("utf-8"),
    #     headers={"Content-Type": "application/json"},
    #     method="POST"
    # )

    # try:
    #     # Run blocking HTTP request in a worker thread
    #     response = await __import__("asyncio").to_thread(
    #         urlopen, request, timeout=10
    #     )
    #     with response:
    #         result = response.read().decode("utf-8")


    #     )
    # except Exception as e:
    #     await interaction.response.send_message(
    #         f"Order failed: {e}",
    #         ephemeral=True
    #     )


#region QOL functions
@log_errors
async def get_channel(channel_id:int):
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} was not found.")
    return channel

@log_errors
async def get_username(user_id:int):
    username = client.get_user(user_id).display_name
    return username

@log_errors
async def send_message(channel_id:int,msg:str,*args, **kwargs):
    #print(f"Discord: Send {msg} in {channel_id}")
    channel = await get_channel(int(channel_id))
    return await channel.send(msg, *args, **kwargs, allowed_mentions=discord.AllowedMentions(everyone=True,users=False,roles=False,))


#region Orders
@log_errors
async def create_order(order_id:str):
    print(f"Discord: Creating order {order_id} in {category_id}")
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)

    category = client.get_channel(category_id)
    if not isinstance(category, discord.CategoryChannel):
        raise ValueError(f"Category {category_id} was not found.")
    
    guild = category.guild

    name = config["discord"]["order_channel_name"].format(order_id=order_id)
    
    channel = await guild.create_text_channel(name=name, category=category, reason="Create order",)
    await channel.edit(sync_permissions=True)
    
    order.setdefault("discord", {})
    order["discord"]["channel"] = channel.id
    
    with open(f"orders/{order_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(order, indent=4))
    
    return channel.id

@log_errors
async def remove_order(order_id:str):
    print(f"Discord: Removing order {order_id} in {category_id}")
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)

    channel = await get_channel(int(order["discord"]["channel"]))
    await channel.delete()
    
    return

class RequestOrderPrompt(discord.ui.View):
    def __init__(self, order_id, channel_id):
        super().__init__(timeout=config["discord"]["order_timeout"])
        self.order_id = order_id
        self.result_future = asyncio.get_running_loop().create_future()
        self.channel_id = channel_id
    
    @log_errors
    async def wait_for_result(self) -> str:
        return await self.result_future

    @log_errors
    async def on_timeout(self):
        channel = await get_channel(self.channel_id)
        await channel.delete(reason="Timedout order")
        self.result_future.set_result("timeout")
        
    @log_errors
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="order:accept")
    async def accept_order(self, interaction: discord.Interaction, button: discord.ui.Button): 
        await interaction.response.edit_message(view=None)
        self.result_future.set_result("accepted")
    
    @log_errors
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="order:reject")
    async def reject_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        await interaction.channel.delete(reason="Remove order")
        self.result_future.set_result("rejected")

@log_errors
async def send_order_request(order_id:str):
    print(f"Discord: Loading payment request for order {order_id}")
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)
    
    channel_id = order["discord"]["channel"]
    username = order["user"]["name"]
    address = order["user"]["address"]
    phone = order["user"]["phone"]
    restaurant = order["order"]["restaurant"]
    
    msg_items = ""
    for i in order["order"]["items"]:
        item = i["name"]
        msg_items += f"- {item}\n"
        for ii in i["options"]:
            msg_items += f"> {ii}\n"
    
    msg:str = f"# Please aprove **@{username}**'s order!\nㅤ\n**RESTAURANT**\n{restaurant}\n\n**ITEMS**\n{msg_items}\n**USER**\n- {address}\n- {phone}\n\n-# @here This bot was made by [Kaasijs](<https://github.com/Kaasijs>). UwU"
    
    view = RequestOrderPrompt(order_id, channel_id)
    await send_message(channel_id, msg=msg, view=view)
    result = await view.wait_for_result()
    
    return result # timeout , accepted , rejected

class RequestPaymentPrompt(discord.ui.View):
    def __init__(self, order_id, channel_id, payment_link):
        super().__init__(timeout=config["discord"]["payment_timeout"])
        self.payment_link = payment_link
        self.order_id = order_id
        self.add_item(discord.ui.Button(label="Ideal / Wero", style=discord.ButtonStyle.link, url=payment_link))
        self.channel_id = channel_id

    @log_errors
    async def on_timeout(self):
        channel = await get_channel(self.channel_id)
        await channel.delete(reason="Timedout order")

@log_errors
async def send_payment_request(order_id:int, payment_link: str):
    print(f"Discord: Loading payment request for order {order_id}")
    
    with open(f"orders/{order_id}.json", "r", encoding="utf-8") as f:
        order = json.load(f)
        
    channel_id = order["discord"]["channel"]
    channel = await get_channel(channel_id)

    username = order["user"]["name"]
    address = order["user"]["address"]
    phone = order["user"]["phone"]
    
    msg:str = f"[Payment needed!]]({payment_link})\n-# @here This bot was made by [Kaasijs](<https://github.com/Kaasijs>). UwU"
    
    view = RequestPaymentPrompt(order_id, channel_id, payment_link)
    await send_message(channel_id, msg=msg, view=view)

