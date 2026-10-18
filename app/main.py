from config import config
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pprint
import bot
import discordbot
import uuid
import json
import os
from models import *

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    if config["discord"]["token"] =="": print("Discord Disabled"); return;
    token = config["discord"]["token"]
    discordbot_task = asyncio.create_task(discordbot.client.start(token))
    bot.discordbot = discordbot
    yield
    await discordbot.client.close()
    await discordbot_task

# Do api stuff
app = FastAPI(title="Roobot Food Order API blabla~ UwU", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "online", "message": "Roobot Food Order API is running UwU"}

@app.post("/order")
async def create_order(payload:OrderPayload):
    order = payload.model_dump()    
    using_discord = config["discord"]["token"] !=""
    if discordbot.client.is_ready() or not using_discord:
        # If username is a profile index (user.json)
        if (not "address" in order) or (not "phone" in order):
            username = order["user"]["name"]
            if Path(f"users/{username}.json").exists():
                with open(f"users/{username}.json", "r", encoding="utf-8") as f:
                    user = json.load(f)
                
                order["user"] = user
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = {
                        "error": "Discord Intergration didnt have user info",
                        "message": "Please make user do /user to create a user info file before ordering"
                    })
        
        #Create order
        order_id = str(uuid.uuid4()).replace('-', '')[:8]
        with open(f"orders/{order_id}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(order, indent=4))
        
        pprint.pp(f"created order {order_id} : ")
        pprint.pp(order)
        
        try:
            if discordbot != None:
                await discordbot.create_order(order_id)
            await bot.order(order_id)
        
        except Exception:
            await discordbot.remove_order(order_id)
            
            if os.path.exists(f"orders/{order_id}.json"):
               os.remove(f"orders/{order_id}.json")
            
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "error": "Discord Intergration was not ready",
                    "message": "Try again in a few sec, sorry qwq."
                })
        
        if using_discord and config["discord"]["order_timeout"] != 0:
                await asyncio.sleep(config["discord"]["order_timeout"])
        else:
            await asyncio.sleep(600)
            
        if using_discord:
            await discordbot.remove_order(order_id)
        
        if os.path.exists(f"orders/{order_id}.json"):
            os.remove(f"orders/{order_id}.json")
    
        return HTTPException(status_code=status.HTTP_200_OK)
    
    else:
        raise HTTPException(
        status_code = status.HTTP_425_TOO_EARLY,
        detail = {
            "error": "Discord Intergration was not ready",
            "message": "Try again in a few sec, sorry qwq."
        })

@app.post("/user")
async def create_user(payload:UserProfile):
    user = payload.model_dump()
    user_name = user["name"]
    with open(f"users/{user_name}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(user, indent=4))

@app.get("/order/{order_id}")
async def get_order(order_id:str):
    with open(f"orders/{order_id}.json", 'r') as f:
        order = json.load(f)
    
    order["user"] = "Removed for privacy"
    
    return order