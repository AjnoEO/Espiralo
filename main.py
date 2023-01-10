import interactions
import os
import keep_alive
import logging

TOKEN = os.environ['BOT_TOKEN']
GUILD = os.environ['GUILD_ID']

logging.basicConfig(level=logging.DEBUG)
bot = interactions.Client(token=TOKEN)
    
#bot.load("kogoj.rolaro")
#bot.load("kogoj.lingvo")
bot.load("kogoj.testo")
keep_alive.keep_alive()
bot.start()

@bot.event
async def on_ready():
    print("La roboto enretiĝis.")