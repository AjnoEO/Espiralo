import interactions
import os
from replit import db
import komandaroj.cxiaj as c
from PIL import Image
from urllib.request import urlopen
import re
from datetime import datetime

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
USERNAME = str(os.environ['USERNAME_DISCRIMINATOR'])
TENOR_KEY = str(os.environ['TENOR_KEY'])
TENOR_CLIENT_KEY = str(os.environ['TENOR_CLIENT_KEY'])
ID = int(os.environ['BOT_ID'])

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
        db[f"steltabulo_{ctx.guild.id}_emogxio_inta"] = db[
            f"steltabulo_{ctx.guild.id}_emogxio"]
        del db[f"steltabulo_{ctx.guild.id}_emogxio"]
        if (f"steltabulo_{ctx.guild.id}_atentendaj"
                not in db.prefix("steltabulo_")):
            db[f"steltabulo_{ctx.guild.id}_atentendaj"] = ""

    # PRITRAKTADO DE ALDONOJ DE REAGUMOJ
    @interactions.extension_listener()
    async def on_message_reaction_add(self, reagumo: interactions.MessageReaction):

        gilda_id = reagumo.guild_id
        if (f"steltabulo_{gilda_id}_kanalo" in db.prefix("steltabulo_") and reagumo.user_id != ID):
            if ((self.agordmesagxo != None) and (reagumo.message_id == self.agordmesagxo.id)):
                kanalo = await self.agordmesagxo.get_channel()
                await self.agordmesagxo.edit(
                    f"**Sukcese agordite**\n" \
                    f"> _Kanalo:_ <#{kanalo.id}>\n" \
                    f"> _Minimume da steloj:_ {db[f'steltabulo_{gilda_id}_kvanto']}\n" \
                    f"> _La emoĝio:_ {reagumo.emoji} (ID: `{reagumo.emoji.id if (reagumo.emoji.id != None) else 'Nula'}`, nomo: `{reagumo.emoji.name}`)"
                )
                self.agordmesagxo = None
                db[f"steltabulo_{str(gilda_id)}_emogxio"] = \
                    f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
                if db[f"steltabulo_{gilda_id}_emogxio_inta"] != db[f"steltabulo_{gilda_id}_emogxio"]:
                    db[f"steltabulo_{gilda_id}_atentendaj"] = ""

            elif (f"steltabulo_{gilda_id}_emogxio" in db.prefix("steltabulo_")):
                e_id = db[f"steltabulo_{gilda_id}_emogxio"]
                emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)

                if (str(reagumo.emoji) == str(emogxio)):
                    mesagxo = await interactions.get(
                        self.client,
                        interactions.Message,
                        object_id=reagumo.message_id,
                        parent_id=reagumo.channel_id,
                        force="http"
                    )
                    kvanto = await c.reaguma_kvanto(mesagxo, emogxio)
                    reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
                    uzantnomoj = [f"{u.username}#{u.discriminator}" for u in reagumintoj]

                    if (kvanto >= int(db[f"steltabulo_{gilda_id}_kvanto"]) and USERNAME not in uzantnomoj):

                        kanalo = await interactions.get(
                            self.client,
                            interactions.Channel,
                            object_id=db[f"steltabulo_{gilda_id}_kanalo"]
                        )
                        mesagxkanalo = await mesagxo.get_channel()
                        ano = await interactions.get(
                            self.client,
                            interactions.Member,
                            object_id=mesagxo.author.id,
                            parent_id=gilda_id
                        )
                        avataro = ano.get_avatar_url(gilda_id)
                        if (avataro == None):
                            avataro = mesagxo.author.avatar_url
                        nomo = ano.nick
                        if (nomo == None):
                            nomo = mesagxo.author.username
                        if mesagxo.author.bot:
                            nomo = "🤖 [ROBOTO] " + nomo

                        aldonajxoj_teksto = "> _Tipoj de la aldonajxoj:_"
                        bildoj = []
                        gifbildoj = []
                        videoj = []
                        bilda_ligilo = None
                        videa_ligilo = None
                        enhavo = mesagxo.content
                        aldonajxoj = mesagxo.attachments
                        for a in aldonajxoj:
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
                                #if (videa_ligilo == None):
                                #    videa_ligilo = a.url
                                videoj.append(a.url)

                        bilda_kvanto = len(bildoj)
                        kvanto_de_alio = len(aldonajxoj) - len(videoj) - len(gifbildoj) - bilda_kvanto
                        if (bilda_ligilo != None):
                            kvanto_de_alio -= 1

                        tenoraj_ligiloj = re.findall(
                            r"\bhttps?://tenor\.com/view/[a-zA-Z0-9-]+\b",
                            enhavo
                        )
                        if (len(tenoraj_ligiloj) > 0):
                            for l in tenoraj_ligiloj:
                                if (bilda_ligilo == None):
                                    bilda_ligilo = c.tenora_gifo(l)
                                else:
                                    gifbildoj.append(l)
                            if (enhavo == tenoraj_ligiloj[0]):
                                enhavo = ""
                        diskordaj_gif_ligiloj = re.findall(
                            r"\bhttps?://media\.discordapp\.net/attachments/[a-zA-Z0-9/-]+\.gif\b", 
                            enhavo
                        )
                        if (len(diskordaj_gif_ligiloj) > 0):
                            for l in diskordaj_gif_ligiloj:
                                if (bilda_ligilo == None):
                                    bilda_ligilo = l
                                else:
                                    gifbildoj.append(l)
                            if (mesagxo.content == diskordaj_gif_ligiloj[0]):
                                enhavo = ""
                        #jutubaj_kodoj = re.findall(r"\b(https?://www.youtube.com/watch\?v=([a-zA-Z0-9]+))", mesagxo.content)
                        #jutubaj_kodoj.extend(re.findall(r"\b(https?://youtu.be/([a-zA-Z0-9]+))", mesagxo.content))
                        #http://img.youtube.com/vi/%s/0.jpg
                        plusenhavoj = mesagxo.embeds
                        if (plusenhavoj != None):
                            for p in plusenhavoj:
                                if p.type == 'video':
                                    if (bilda_ligilo == None):
                                        bilda_ligilo = p.thumbnail.url
                                        videa_provizanto = p.provider.name
                                        videa_nomo = p.title
                                        videa_kanalnomo = p.author.name
                                        enhavo += f"""\n```ansi\n\u001b[2;31m\u001b[4;31m\u001b[4;30m\u001b[0m\u001b[4;31m\u001b[0m\u001b[2;31m\u001b[0m\u001b[0;2m\u001b[4;2m\u001b[4;2m\u001b[0;2m\u001b[0m\u001b[0m\u001b[0m\u001b[0;2m{videa_provizanto}\n\n\u001b[0;37m\u001b[1;37m{videa_kanalnomo}\u001b[0m\u001b[0;37m\u001b[0m\n\u001b[0;34m\u001b[1;34m\u001b[4;34m\u001b[1;34m{videa_nomo}\u001b[0m\u001b[4;34m\u001b[0m\u001b[1;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\u001b[0m\u001b[2;34m\u001b[1;34m\u001b[0;34m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[1;34m\u001b[0m\u001b[2;34m\u001b[0m\n```"""
                                    else:
                                        videoj.append(p.url)

                        subteksto = "+ "
                        gifbilda_kvanto = len(gifbildoj)
                        videa_kvanto = len(videoj)
                        subteksto += f"{bilda_kvanto} bildo{'j' if bilda_kvanto > 1 else ''}, " if bilda_kvanto > 0 else ""
                        subteksto += f"{gifbilda_kvanto} gif-bildo{'j' if gifbilda_kvanto > 1 else ''}, " if gifbilda_kvanto > 0 else ""
                        subteksto += f"{videa_kvanto} video{'j' if videa_kvanto > 1 else ''}, " if videa_kvanto > 0 else ""
                        subteksto += f"{kvanto_de_alio} dosiero{'j' if kvanto_de_alio > 1 else ''}, " if kvanto_de_alio > 0 else ""
                        subteksto = subteksto[:-2]

                        #if (len(bildoj) != 0):
                        #    bildo = c.kunigi(bildoj)
                        #    bd_nomo = f"bildo_{kanalo.id}_{mesagxo.id}.jpg"
                        #    bildo.save(bd_nomo)

                        enhavo = f"[⮪ La originalo]({mesagxo.url})\n" + enhavo
                        dosiero = interactions.File(filename="bildoj/krisigno_sen_fono.png")
                        plusenhavo = interactions.Embed(
                            author=interactions.EmbedAuthor(
                                name=nomo,
                                icon_url=avataro,
                            ),
                            description=enhavo,
                            timestamp=mesagxo.timestamp,
                            color=0x1EC34B,
                            image=interactions.EmbedImageStruct(url=bilda_ligilo) if (bilda_ligilo != None) else None,
                            video=interactions.EmbedImageStruct(url=videa_ligilo) if (videa_ligilo != None) else None,
                            footer=interactions.EmbedFooter(
                                text=subteksto,
                                icon_url="attachment://krisigno_sen_fono.png"
                            ) if subteksto != "" else None,
                        )
                        if (not (mesagxo.embeds == None or len(mesagxo.embeds) == 0)):
                            print(str(mesagxo.embeds[0]))
                        steltabula_mesagxo = await kanalo.send(
                            content=f"{f'<#{mesagxkanalo.parent_id}> 🢧 ' if (mesagxkanalo.type in range(10, 13)) else ''}<#{mesagxkanalo.id}>\n" \
                            f"{emogxio} **x{kvanto}**\n",
                            embeds=plusenhavo,
                            files=dosiero if subteksto != "" else interactions.MISSING,
                        )
                        tempo = datetime.utcnow()
                        db[f"steltabulo_{gilda_id}_atentendaj"] += f"|{tempo.timestamp()}:{mesagxkanalo.id}.{mesagxo.id}:{kanalo.id}.{steltabula_mesagxo.id}"

                        await mesagxo.create_reaction(emogxio)

                    else:
                        steltabule = c.steltabula_mesagxo(
                            gilda_id, 
                            reagumo.channel_id, 
                            reagumo.message_id
                        )
                        if (steltabule != None):
                            mesagxo = await interactions.get(
                                self.client,
                                interactions.Message,
                                object_id=steltabule[1],
                                parent_id=steltabule[0],
                                force="http",
                            )
                            originala = await interactions.get(
                                self.client,
                                interactions.Message,
                                object_id=reagumo.message_id,
                                parent_id=reagumo.channel_id,
                                force="http",
                            ) 
                            emogxio = await c.emogxio_el_datumbazo(
                                self, 
                                gilda_id,
                                db[f"steltabulo_{gilda_id}_emogxio"]
                            )
                            kvanto = await c.reaguma_kvanto(
                                originala,
                                emogxio,
                                sen_roboto=True
                            )
                            teksto = mesagxo.content
                            await mesagxo.edit(
                                content=re.sub(
                                    re.escape(f"{emogxio}") + r"\s\*\*x\d+\*\*\b",
                                    f"{emogxio} **x{str(kvanto)}**", 
                                    teksto
                                )
                            )

    @interactions.extension_listener()
    async def on_message_reaction_remove(self, reagumo: interactions.MessageReaction):
        
        gilda_id = reagumo.guild_id
        if (f"steltabulo_{gilda_id}_emogxio" in db.prefix("steltabulo_") and reagumo.user_id != ID):
            e_id = db[f"steltabulo_{gilda_id}_emogxio"]
            emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)
            if (str(reagumo.emoji) == str(emogxio)):
                steltabule = c.steltabula_mesagxo(
                    reagumo.guild_id,
                    reagumo.channel_id,
                    reagumo.message_id
                )
                if (steltabule != None):
                    mesagxo = await interactions.get(
                        self.client,
                        interactions.Message,
                        object_id=steltabule[1],
                        parent_id=steltabule[0],
                        force="http",
                    )
                    originala = await interactions.get(
                        self.client,
                        interactions.Message,
                        object_id=reagumo.message_id,
                        parent_id=reagumo.channel_id,
                        force="http",
                    ) 
                    emogxio = await c.emogxio_el_datumbazo(
                        self, 
                        gilda_id, 
                        db[f"steltabulo_{gilda_id}_emogxio"]
                    )
                    kvanto = await c.reaguma_kvanto(
                        originala,
                        emogxio,
                        sen_roboto=True
                    )
                    teksto = mesagxo.content
                    await mesagxo.edit(
                        content=re.sub(
                            re.escape(f"{emogxio}") + r"\s\*\*x\d+\*\*\b",
                            f"{emogxio} **x{str(kvanto)}**", 
                            teksto
                        )
                    )


def setup(client):
    Steltabulo(client)
