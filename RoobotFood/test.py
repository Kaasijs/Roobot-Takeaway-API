import discordbot

discordbot.send_payment_request(msg="w", payment_link="https://kaasijs.com", order_id=0, timeout=10)
print (discordbot.status)