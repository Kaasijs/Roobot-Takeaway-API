import json
import discord
import time
from enum import Enum

class Status(Enum):
    Initialized = 1
    AwaitingResponse = 2
    Timedout = 3
    Rejected = 4
    Accepted = 5
    
status = Status.Initialized

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def send_message(channel:int,msg:str):
    class MyClient(discord.Client):
        async def on_ready(self):
            print(f"sending message {msg} as {self.user} in {channel}!")
            await client.get_channel(channel).send(msg)
            return

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(config["discord"]["token"])

def send_payment_request(msg: str, payment_link: str, order_id:int, category_id= int(config["discord"]["category_id"]), guild_id= int(config["discord"]["guild_id"]), timeout=1200):
    global status
    status = Status.AwaitingResponse
    
    start_time = time.time()
    while time.time() - start_time < timeout:    
        class MyClient(discord.Client):
            async def on_ready(self):
                print(f"sending payment request as {self.user} to {category_id} in {guild_id}!")
                
                guild = client.get_guild(int(guild_id))
                if guild is None:
                    raise ValueError(f"Guild {guild_id} not found. Check the guild ID and bot membership.")

                category = guild.get_channel(category_id)
                if not isinstance(category, discord.CategoryChannel):
                    raise ValueError(f"Category {category_id} was not found in guild {guild.id}.")

                channel = await guild.create_text_channel(name=f"🤖・order-{order_id}", category=category, reason="Create order",)
                await channel.edit(sync_permissions=True)
                
                await channel.send(
                    content=f"@here\n{msg}",
                    view=OrderButtons(),
                    allowed_mentions=discord.AllowedMentions(
                        everyone=True,
                        users=False,
                        roles=False,
                    ),
                )
        
        class OrderButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="order:accept")
            async def accept_order(self, interaction: discord.Interaction, button: discord.ui.Button):         
                timeout += 600
                await interaction.channel.send(f"Payment needed UwU\n{payment_link}")
                global status
                status = Status.Accepted
                break
            
            @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="order:reject")
            async def reject_order(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.channel.delete(reason="Remove order")
                global status
                status = Status.Rejected
                
        intents = discord.Intents.default()
        intents.message_content = True

        client = MyClient(intents=intents)
        client.run(config["discord"]["token"])
    
    else:
        status = Status.Timedout
    
    return