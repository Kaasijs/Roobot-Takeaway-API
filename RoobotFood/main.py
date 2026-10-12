import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pprint
import bot
import discordbot
import uuid
import json

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

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

@asynccontextmanager
async def lifespan(app: FastAPI):
    token = config["discord"]["token"]
    discordbot_task = asyncio.create_task(discordbot.client.start(token))
    yield
    await discordbot.client.close()
    await discordbot_task

# Do api stuff
app = FastAPI(title="Roobot Food Order API blabla~ UwU", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "online", "message": "Roobot Food Order API is running UwU"}


class User(BaseModel):
    name:str = Field(examples=["Roobot"])
    address:str = Field(examples=["Torontoweg 101, 1334 KT Almere"])
    phone:str = Field(examples=["+31655555555"])

class Item(BaseModel):
    name: str = Field(examples=["Margherita pizza","Twister meal"])
    options: list[str] = Field(examples=[["26 cm"],["Geen Extra","Friet L","Pepsi Zero Sugar L - Standaard Beker"]])

class Order(BaseModel):
    restaurant:str = Field(examples=["Pizza Xpress","KFC"])
    items:list[Item]

class Payload(BaseModel):
    user:User
    order:Order

@app.post("/order")
def create_order(payload:Payload):
    order = payload.model_dump()
    
    #Create order
    order_id = str(uuid.uuid4()).replace('-', '')[:8]
    with open(f"orders/{order_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(order, indent=4))
    
    pprint.pp(f"created order {order_id} : ")
    pprint.pp(order)
    
    ideal_link:str = bot.order(order_id)
    
    raise HTTPException(
    status_code = status.HTTP_402_PAYMENT_REQUIRED,
    detail = {
        "error": "payment_required",
        "message": "Orders need to be aproved by api host. For API host, contact me kaasijs if you think this is a bug",
        "payment_url": ideal_link,
    })

@app.get("/test")
def create_order(result:str):
    return "test result:" + result