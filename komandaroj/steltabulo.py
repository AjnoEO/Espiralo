import interactions
import os
from replit import db
from komandaroj.cxiaj import reaguma_kvanto, kunigi, tenora_gifo
from PIL import Image
from urllib.request import urlopen
import re

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
USERNAME = str(os.environ['USERNAME_DISCRIMINATOR'])
TENOR_KEY = str(os.environ['TENOR_KEY'])
TENOR_CLIENT_KEY = str(os.environ['TENOR_CLIENT_KEY'])

class Steltabulo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.agordmesagxo: interactions.Message = None

    # KOMANDO /STELTABULO
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD)
    async def steltabulo(self, ctx):
        return None

    # /STELTABULO AGORDI
    @steltabulo.subcommand()
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn")
    @interactions.option(
        description=
        "Kiom da steloj estu por ke la afiŝo ensteltabuliĝu. Defaŭlte: 4")
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

    # PRITRAKTADO DE ALDONOJ DE REAGUMOJ
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
                db[f"steltabulo_{str(reagumo.guild_id)}_emogxio"] = \
                f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"

            elif (f"steltabulo_{reagumo.guild_id}_emogxio" in db.prefix("steltabulo_")):
                e_id = db[f"steltabulo_{reagumo.guild_id}_emogxio"]
                if (e_id[0] == 'i'):
                    emogxio = await interactions.get(
                        self.client,
                        interactions.Emoji,
                        object_id=e_id[1:],
                        parent_id=reagumo.guild_id)
                else:
                    emogxio = interactions.Emoji(name=e_id[1:])

                if (str(reagumo.emoji) == str(emogxio)):
                    mesagxo = await interactions.get(
                        self.client,
                        interactions.Message,
                        object_id=reagumo.message_id,
                        parent_id=reagumo.channel_id,
                        force="http")
                    kvanto = reaguma_kvanto(mesagxo, emogxio)
                    reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
                    uzantnomoj = [f"{u.username}#{u.discriminator}" for u in reagumintoj]

                    if (kvanto >= int(db[f"steltabulo_{reagumo.guild_id}_kvanto"]) and USERNAME not in uzantnomoj):

                        kanalo = await interactions.get(
                            self.client,
                            interactions.Channel,
                            object_id=db[f"steltabulo_{reagumo.guild_id}_kanalo"])
                        mesagxkanalo = await mesagxo.get_channel()
                        gildaid = reagumo.guild_id
                        ano = await interactions.get(
                            self.client,
                            interactions.Member,
                            object_id=mesagxo.author.id,
                            parent_id=gildaid)
                        avataro = ano.get_avatar_url(gildaid)
                        if (avataro == None):
                            avataro = mesagxo.author.avatar_url
                        nomo = ano.nick
                        if (nomo == None):
                            nomo = mesagxo.author.username
                        aldonajxoj_teksto = "> _Tipoj de la aldonajxoj:_"
                        bildoj = []
                        gifbildoj = []
                        videoj = []
                        bilda_ligilo = None
                        videa_ligilo = None
                        forigi_mesagxon = False
                        aldonajxoj = mesagxo.attachments
                        for a in aldonajxoj:
                            print("->")
                            aldonajxoj_teksto += f"\n> {a.content_type} ({a.content_type[:5]})"
                            if (a.content_type[:6] == "image/"):
                                if (bilda_ligilo == None):
                                    bilda_ligilo = a.url
                                #bildoj.append(Image.open(urlopen(a.url)))
                                elif (a.content_type == "image/gif"):
                                    gifbildoj.append(a.url)
                                else:
                                    bildoj.append(a.url)
                            if (a.content_type[:6] == "video/"):
                                if (videa_ligilo == None):
                                    videa_ligilo = a.url
                                videoj.append(a.url)
                        
                        bilda_kvanto = len(bildoj)
                        videa_kvanto = len(videoj)
                        kvanto_de_alio = len(aldonajxoj) - videa_kvanto - len(gifbildoj) - bilda_kvanto
                        if (bilda_ligilo != None):
                            kvanto_de_alio -= 1
                        
                        tenoraj_ligiloj = re.findall(r"\bhttps?://tenor\.com/view/[a-zA-Z0-9-]+\b", mesagxo.content)
                        if (len(tenoraj_ligiloj)>0):
                            for l in tenoraj_ligiloj:
                                if (bilda_ligilo == None):
                                    bilda_ligilo = tenora_gifo(l)
                                else:
                                    gifbildoj.append(l)
                            if (mesagxo.content == tenoraj_ligiloj[0]):
                                forigi_mesagxon = True
                        diskordaj_gif_ligiloj = re.findall(r"\bhttps?://media\.discordapp\.net/attachments/[a-zA-Z0-9/-]+\.gif\b", mesagxo.content)
                        if (len(diskordaj_gif_ligiloj)>0):
                            for l in diskordaj_gif_ligiloj:
                                if (bilda_ligilo == None):
                                    bilda_ligilo = l
                                else:
                                    gifbildoj.append(l)
                            if (mesagxo.content == diskordaj_gif_ligiloj[0]):
                                forigi_mesagxon = True

                        subteksto = "+ "
                        gifbilda_kvanto = len(gifbildoj)
                        subteksto += f"{bilda_kvanto} bildo{'j' if bilda_kvanto > 1 else ''}, " if bilda_kvanto > 0 else ""
                        subteksto += f"{gifbilda_kvanto} gif-bildo{'j' if gifbilda_kvanto > 1 else ''}, " if gifbilda_kvanto > 0 else ""
                        subteksto += f"{videa_kvanto} video{'j' if videa_kvanto > 1 else ''}, " if videa_kvanto > 0 else ""
                        subteksto += f"{kvanto_de_alio} dosiero{'j' if kvanto_de_alio > 1 else ''}, " if kvanto_de_alio > 0 else ""
                        subteksto = subteksto[:-2]
                        
                        #if (len(bildoj) != 0):
                        #    bildo = kunigi(bildoj)
                        #    bd_nomo = f"bildo_{kanalo.id}_{mesagxo.id}.jpg"
                        #    bildo.save(bd_nomo)

                        dosiero = interactions.File(filename="bildoj/krisigno_sen_fono.png")
                        plusenhavo = interactions.Embed(
                            author=interactions.EmbedAuthor(
                                name=nomo,
                                icon_url=avataro,
                            ),
                            description=mesagxo.content if not forigi_mesagxon else None,
                            timestamp=mesagxo.timestamp,
                            color=0x1EC34B,
                            image=interactions.EmbedImageStruct(url=bilda_ligilo) if (bilda_ligilo != None) else None,
                            video=interactions.EmbedImageStruct(url=videa_ligilo) if (videa_ligilo != None) else None,
                            footer=interactions.EmbedFooter(
                                text=subteksto,
                                icon_url="attachment://krisigno_sen_fono.png"
                            ) if subteksto != "" else None,
                        )
                        print("La subteksto:")
                        print(subteksto)
                        await kanalo.send(
                            content=f"<#{mesagxkanalo.id}> {mesagxo.url}\n" \
                            f"{emogxio} x{kvanto}\n" \
                            f"`Tipo de la mesaĝo: {mesagxo.type}`\n" \
                            + aldonajxoj_teksto,
                            embeds=plusenhavo,
                            files=dosiero if subteksto != "" else interactions.MISSING,
                        )
                        
                        await mesagxo.create_reaction(emogxio)


def setup(client):
    Steltabulo(client)
