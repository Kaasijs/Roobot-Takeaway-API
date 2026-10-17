import json
from typing import Literal
from pydantic import BaseModel, HttpUrl
import pprint
from pathlib import Path


class CreditCard(BaseModel):
    number: str = "0000 0000 0000 0000"
    expires: str = "06/29"
    cvv: str = "000"
    name: str = "Placeholder"

class Platform(BaseModel):
    url: str = "https://www.thuisbezorgd.nl/"

class Imap(BaseModel):
    email: str = "mail@example.com"
    password: str = ""

class Discord(BaseModel):
    token: str = ""
    guild_id: int = 0
    category_id: int = 0
    order_channel_name: str = "order-{order_id}"
    order_timeout: int = 600
    payment_timeout: int = 1200

class Config(BaseModel):
    need_approval: bool = True
    payment_method: Literal["ideal"] | dict[str, CreditCard]
    platform: Platform
    imap: Imap
    discord: Discord


my_file = Path("config/config.json")
if my_file.is_file():
    try:
        with open("config/config.json", encoding="utf-8") as f:
            config = config = Config.model_validate(json.load(f)).model_dump(by_alias=True)
        print("INFO:     Found config:")
        pprint.pp(config)
    except Exception:
        try:
            with open("example-config.json", "r", encoding="utf-8") as f:
                example_config = json.load(f)
        except:
            raise Exception("Docker directory misconfigured. please ref to doc")
        else:
            example_config = pprint.pformat(example_config)
            raise Exception(f"There was no /app/config/config.json present! \nPlease check out the docs for more info \nExample config:\n{example_config}")

else:
    config = Config.model_dump()
    with open(f"config/config.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(config, indent=4))