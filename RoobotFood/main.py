from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pprint
import bot

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

# Do api stuff
app = FastAPI(title="Roobot Food Order API blabla~ UwU", version="1.0.0")

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

    pprint.pp("new order received:")
    pprint.pp(order)
    
    ideal_link:str = bot.order(order)
    
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