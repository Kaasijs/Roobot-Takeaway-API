from pydantic import BaseModel, Field
from pathlib import Path

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

class OrderPayload(BaseModel):
    user:User
    order:Order

ORDERS_DIR = Path("orders")
ORDERS_DIR.mkdir(parents=True, exist_ok=True)

USERS_DIR = Path("users")
USERS_DIR.mkdir(parents=True, exist_ok=True)
