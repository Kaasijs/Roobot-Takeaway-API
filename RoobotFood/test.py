import asyncio
import discordbot
import json
import traceback

with open('config.json', 'r') as f:
    config = json.load(f)

async def main():
    async with discordbot.client:
        await discordbot.client.start(config["discord"]["token"])

@discordbot.client.event
async def on_ready():
    print("ready")
    order_id = "0c4f2946"
    
    await discordbot.create_order(order_id)
    
    request = await discordbot.send_order_request(order_id)
    if request == "accepted":
        
        await discordbot.send_payment_request(order_id,"https://kaasijs.com")
    
    else:  
        await discordbot.client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except Exception:
        traceback.print_exc()