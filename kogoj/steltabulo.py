import interactions
import os
from replit import db

GUILD = os.environ['GUILD_ID']

class Steltabulo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD
    )
    async def steltabulo(self, ctx):
        return None

    @steltabulo.subcommand
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
    )
    @interactions.option(
        description="Kiom da steloj estu por ke la afiŝo ensteltabuliĝu"
    )
    async def agordi(self, ctx, kanalo: interactions.Channel, kvanto: int):
        """Agordi la steltabulon (uzeblas ankaŭ por la unua aktivigo)"""
        await ctx.send(f"Ricevite: \n> {str(kanalo)}\n> {str(kvanto)}")

def setup(client):
    Steltabulo(client)