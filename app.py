from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pprint
import json
import bot

app = FastAPI(title="Roobot Food Order API blabla~ UwU", version="1.0.0")

@app.get("/")
async def root():
    return {"status": "online", "message": "Roobot Food Order API is running UwU"}

with open('order.json', 'r') as f:
    defualt_order_details = json.load(f)

class User(BaseModel):
    name:str = Field(examples=["Roobot"])
    address:str = Field(examples=["Torontoweg 101, 1334 KT Almere"])
    phone:str = Field(examples=["+31655555555"])

class Item(BaseModel):
    name: str = Field(examples=["Twister meal","Margherita pizza"])
    options: list[str] = Field(examples=[["Geen Extra","Friet L","Pepsi Zero Sugar L - Standaard Beker"],["26 cm"]])

class Order(BaseModel):
    restaurant:str = Field(examples=["KFC","Pizza Xpress"])
    items:list[Item]

class Payload(BaseModel):
    user:User
    order:Order

@app.post("/order")
def create_order(payload:Payload):
    order_details = defualt_order_details
    payload_dict = payload.model_dump()
    order_details["order"] = payload_dict["order"]
    order_details["user"] = payload_dict["user"]

    pprint.pp(order_details)
    
    ideal_link = bot.order(order_details)
    raise HTTPException(status_code=402, detail=f"Payment needed on {ideal_link}")

@app.get("/test")
def create_order(result:str):
    return "test result:" + result