import interactions
import os
import keep_alive
import logging

TOKEN = str(os.environ['BOT_TOKEN'])
GUILD = int(os.environ['ESPERANTO_GUILD_ID'])

logging.basicConfig(level=logging.DEBUG)
bot = interactions.Client(token=TOKEN)
    
#bot.load("kogoj.rolaro")
#bot.load("kogoj.lingvo")
bot.load("komandaroj.testo")
bot.load("komandaroj.steltabulo")
keep_alive.keep_alive()
bot.start()

@bot.event
async def on_ready():
    print("La roboto enretiĝis.")