<p align="center"><img src="https://kaasijs.github.io/assets/roobot-food-api-cover.png" width="100%"></p>

# Installation with Docker

## Requirements
1. Docker installed and running.
2. A directory on your host machine to store application data. for example:
``/opt/roobotfoodapi/app/config``
3. Port ``8000`` open

## Configure directorys
1. Create a working directory like ``/opt/roobotfoodapi/app/``
2. Create a config directory like ``/opt/roobotfoodapi/app/config``
3. Copy ``/app/config/example-config.json`` from github and rename it to ``config.json`` inside of the config directory
like ``/opt/roobotfoodapi/app/config/config.json`` for testing.

## Runing the API
### Terminal
```
docker run -d \
  --init \
  --shm-size=2g \
  -p 8000:8000 \
  --name roobot-food-api \
  --restart unless-stopped \
  -v /opt/roobotfoodapi/app/config:/app/config \
  -v /opt/roobotfoodapi/app/orders:/app/orders \
  -v /opt/roobotfoodapi/app/users:/app/users \
  kaasijs/roobotfoodapi:latest
```
### Compose
1. Create a ``docker-compose.yml`` file containing:
```
services:
  roobot-food-api:
    image: kaasijs/roobotfoodapi:latest
    container_name: roobot-food-api
    init: true
    shm_size: 2gb
    ports:
      - "8000:8000"
    volumes:
      - /opt/roobotfoodapi/app/config:/app/config
      - /opt/roobotfoodapi/app/orders:/app/orders
      - /opt/roobotfoodapi/app/users:/app/users
    restart: unless-stopped
```
2. run
``docker compose up -d``

# Access the API
The API is available at:
http://localhost:8000/docs#/default/create_order_order_post

# Config
Please refure to ``/app/config/example-config``

## Payment types
all the payment type the bot can work with right now:

### Ideal
```
"payment_method":"Ideal"
```
- For now You need **Approvals** and **Discord** working for this to work properly!

### Creditcard
```
"payment_method":{
    "creditcard":{
        "number":"0000 0000 0000 0000",
        "expires":"06/29",
        "cvv":"000",
        "cc-name":"Test Devlopment Card"
    }},
```
- Works as long as card is valid

## imap
```
"imap":{
    "email":"mail@example.com",
    "password":""
},
```
Just Eats TakeAWay sends a verification code via email. so the bot needs an working imap mail to work.
- replace email with your own mail
- replace password with that email's password

## Discord
```
"discord":{
    "token":"",
    "guild_id":0,
    "category_id":0,
    "order_channel_name":"order-{order_id}",
    "order_timeout":600,
    "payment_timeout":1200
}
```
Discord intergration is used for creating user profiles and easy access to ordering API.
- Replace Token with Discord bot Token from Developer Portal.
- Enable Dev mode for discord to find your server/guild id and category id. The bot wil automaticly create channels inside the category when a order is created
- the ``{order_id}`` is a placeholder for the order's uniqe number. you can remove it if you prefure not to use it
- the last _timeout(s) are used for the buttons generated in the channel
they will automaticly delete the chanel when expired


# Build image from source
```git clone https://github.com/seleniumbase/SeleniumBase.git```
```cd /SeleniumBase```
```docker build --no-cache -t seleniumbase-local .```
```cd /app```
```docker build --no-cache -t roobotfood:1.0 .```


## Approval
- ``"need_approval":true`` Will
Ask the approval for all orders posted to the API. Right now you need Discord configured for this to work properly (I am planning on adding Telegram bots as an alternative!)
- ``"need_approval":false`` To skip
