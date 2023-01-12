import interactions
import os
from replit import db
from komandaroj.cxiaj import reaguma_kvanto

GUILD = os.environ['GUILD_ID']

class Steltabulo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.agordmesagxo: interactions.Message = None
        
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD
    )
    async def steltabulo(self, ctx):
        return None

    @steltabulo.subcommand()
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
    )
    @interactions.option(
        description="Kiom da steloj estu por ke la afiŝo ensteltabuliĝu. Defaŭlte: 4"
    )
    async def agordi(self, ctx, kanalo: interactions.Channel, kvanto: int = 4):
        """Agordi la steltabulon (uzeblas ankaŭ por la unua aktivigo)"""
        self.agordmesagxo = await ctx.send(
            f"**Agordado...**\n" \
            f"> _Kanalo:_ <#{kanalo.id}>\n" \
            f"> _Minimume da steloj:_ {kvanto}\n" \
            f"> _La emoĝio:_ `neniu, bonvolu reagumi per la taŭga emoĝio`"
        )
        db[f"steltabulo_{ctx.guild.id}_kanalo"] = str(kanalo.id)
        db[f"steltabulo_{ctx.guild.id}_kvanto"] = str(kvanto)
        del db[f"steltabulo_{ctx.guild_id}_emogxio"]

    @interactions.extension_listener()
    async def on_message_reaction_add(self, reagumo: interactions.MessageReaction):
        if (f"steltabulo_{reagumo.guild_id}_kanalo" in db.prefix("steltabulo_")):
            
            if ((self.agordmesagxo != None) and (reagumo.message_id == self.agordmesagxo.id)):
                kanalo = await self.agordmesagxo.get_channel()
                await self.agordmesagxo.edit(
                    f"**Sukcese agordite**\n" \
                    f"> _Kanalo:_ <#{kanalo.id}>\n" \
                    f"> _Minimume da steloj:_ {db[f'steltabulo_{reagumo.guild_id}_kvanto']}\n" \
                    f"> _La emoĝio:_ {reagumo.emoji} (ID: `{reagumo.emoji.id if (reagumo.emoji.id != None) else 'Nula'}`, nomo: `{reagumo.emoji.name}`)"
                )
                self.agordmesagxo = None
                db[f"steltabulo_{str(reagumo.guild_id)}_emogxio"] = f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
            
            elif (f"steltabulo_{reagumo.guild_id}_emogxio" in db.prefix("steltabulo_")):
                e_id = db[f"steltabulo_{reagumo.guild_id}_emogxio"]
                if (e_id[0] == 'i'): 
                    emogxio = await interactions.get(self.client, 
                        interactions.Emoji, 
                        object_id=e_id[1:], 
                        parent_id=reagumo.guild_id)
                emogxinomo = e_id[1:] if (e_id[0] == 'n') else emogxio.name
                if (reagumo.emoji.name == emogxinomo):
                    mesagxo = await interactions.get(self.client, 
                        interactions.Message, 
                        object_id=reagumo.message_id, 
                        parent_id=reagumo.channel_id)
                    kvanto = reaguma_kvanto(mesagxo, emogxinomo)
    
                    if (kvanto >= int(db[f"steltabulo_{reagumo.guild_id}_kvanto"])):
                        kanalo = await interactions.get(self.client, interactions.Channel, object_id=db[f"steltabulo_{reagumo.guild_id}_kanalo"])
                        
                        if (db[f"steltabulo_{reagumo.guild_id}_emogxio"][0] == 'i'): 
                            sendota_emogxio = str(emogxio)
                        else: 
                            sendota_emogxio = emogxinomo
                        
                        mesagxkanalo = await mesagxo.get_channel()
                        gildaid = reagumo.guild_id
                        ano = await interactions.get(self.client, 
                            interactions.Member, 
                            object_id=mesagxo.author.id, 
                            parent_id=gildaid)
                        avataro = ano.get_avatar_url(gildaid)
                        if (avataro == None):
                            avataro = mesagxo.author.avatar_url
                        nomo = ano.nick
                        if (nomo == None):
                            nomo = mesagxo.author.username
                        plusenhavo = interactions.Embed(
                            author = interactions.EmbedAuthor(
                                name=nomo,
                                #name=mesagxo.author.username,
                                icon_url=avataro,
                                #icon_url=mesagxo.author.avatar_url
                            ),
                            description = mesagxo.content
                        )
                        
                        await kanalo.send(
                            content=f"<#{mesagxkanalo.id}> {mesagxo.url}\n" \
                            f"{sendota_emogxio} x{kvanto}\n" \
                            f"`Tipo de la mesaĝo: {mesagxo.type}`\n",
                            embeds=plusenhavo)
                    #if (reagumo.emoji)


def setup(client):
    Steltabulo(client)