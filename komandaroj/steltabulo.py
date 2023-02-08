import interactions
import os
from replit import db
import komandaroj.cxiaj as c
#from PIL import Image
#from urllib.request import urlopen
import re
from datetime import datetime

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
TENOR_KEY = str(os.environ['TENOR_KEY'])
TENOR_CLIENT_KEY = str(os.environ['TENOR_CLIENT_KEY'])
ID = int(os.environ['BOT_ID'])

async def plusenhavo_el_mesagxo(self, mesagxo: interactions.Message, gilda_id: int):
    ano = None
    avataro = ""
    nomo = ""
    try:
        ano = await interactions.get(
            self.client,
            interactions.Member,
            object_id=mesagxo.author.id,
            parent_id=gilda_id
        )
    except:
        avataro = mesagxo.author.avatar_url
        nomo = mesagxo.author.username
    else:
        avataro = ano.get_avatar_url(gilda_id)
        if (avataro == None):
            avataro = mesagxo.author.avatar_url
        nomo = ano.nick
        if (nomo == None):
            nomo = mesagxo.author.username
    if mesagxo.author.bot:
        nomo = "[🤖] " + nomo

    subteksto_responda = ""
    avataro_respondata = ""
    if (mesagxo.type == interactions.MessageType.REPLY and (mesagxo.message_reference.fail_if_not_exists != True)):
        rjsono = mesagxo._json["referenced_message"]
        ano_respondata = None
        try:
            ano_respondata = await interactions.get(
                self.client,
                interactions.Member,
                object_id=rjsono["author"]["id"],
                parent_id=gilda_id
            )
        except:
            nomo_respondata = rjson["author"]["username"]
        else:
            avataro_respondata = ano_respondata.get_avatar_url(gilda_id)
            if (avataro_respondata == None):
                avataro_respondata = ano.user.avatar_url
            nomo_respondata = ano.nick
            if (nomo_respondata == None):
                nomo_respondata = ano.user.username
            if ano.user.bot:
                nomo_respondata = "[🤖] " + nomo_respondata
        subteksto_responda = f"Responde al {nomo_respondata}"
    
    bildoj = []
    gifbildoj = []
    videoj = []
    bilda_ligilo = None
    videa_ligilo = None
    enhavo = mesagxo.content
    aldonajxoj = mesagxo.attachments
    for a in aldonajxoj:
        if (a.content_type[:6] == "image/"):
            if (bilda_ligilo == None):
                bilda_ligilo = a.url
            elif (a.content_type == "image/gif"):
                gifbildoj.append(a.url)
            else:
                bildoj.append(a.url)
        if (a.content_type[:6] == "video/"):
            videoj.append(a.url)

    kvanto_de_alio = len(aldonajxoj) - len(videoj) - len(gifbildoj) - len(bildoj)
    if (bilda_ligilo != None):
        kvanto_de_alio -= 1

    tenoraj_ligiloj = re.findall(
        r"\bhttps?://tenor\.com/view/[a-zA-Z0-9_-]+\b",
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
    """ r"(\bhttps?://[a-z0-9./_-]+/[a-zA-Z0-9/_-]+\.(jpe?g|png|webp)([&=?][a-zA-Z0-9&=?]*)?\b)", """
    
    plusenhavoj = mesagxo.embeds
    if (plusenhavoj != None):
        for p in plusenhavoj:
            if p.type == 'video':
                if (bilda_ligilo == None):
                    bilda_ligilo = p.thumbnail.url
                    videa_provizanto = p.provider.name
                    videa_nomo = p.title
                    videa_kanalnomo = p.author.name
                    enhavo += f"""\n```ansi\n \u001b[2;31m\u001b[4;31m\u001b[4;30m\u001b[0m\u001b[4;31m\u001b[0m\u001b[2;31m\u001b[0m\u001b[0;2m\u001b[4;2m\u001b[4;2m\u001b[0;2m\u001b[0m\u001b[0m\u001b[0m\u001b[0;2mVideo el {videa_provizanto}\n\n \u001b[0;37m\u001b[1;37m{videa_kanalnomo}\u001b[0m\u001b[0;37m\u001b[0m\n \u001b[0;34m\u001b[1;34m\u001b[4;34m\u001b[1;34m{videa_nomo}\u001b[0m\u001b[4;34m\u001b[0m\u001b[1;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\u001b[0m\u001b[2;34m\u001b[1;34m\u001b[0;34m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[1;34m\u001b[0m\u001b[2;34m\u001b[0m\n```"""
                else:
                    videoj.append(p.url)
            elif p.type == 'image':
                if (bilda_ligilo == None):
                    bilda_ligilo = p.thumbnail.url
                else:
                    if p.thumbnail.proxy_url[-4:] == '.gif':
                        gifbildoj.append(p.url)
                    else:
                        bildoj.append(p.url)
            elif p.type == 'rich':
                if (p.url[:20]=='https://twitter.com/' and p.description != None):
                    tvita_teksto = p.description
                    tvita_nomo = p.author.name
                    tvitaj_sxatumoj = None
                    tvitaj_retvitoj = None
                    for q in p.fields:
                        if (q.name == 'Likes'):
                            tvitaj_sxatumoj = q.value
                        elif (q.name == 'Retweets'):
                            tvitaj_retvitoj = q.value
                    enhavo += f"""\n```ansi\nTwitter\n\u001b[1;2m\u001b[1;37m{tvita_nomo}\u001b[0m\u001b[0m\n\u001b[2;37m{tvita_teksto}\u001b[0m\n\u001b[2;34m\u001b[1;34m{'ŝatumoj     ' if tvitaj_sxatumoj != None else ''}{'retvitoj' if tvitaj_retvitoj != None else ''}\u001b[0m\u001b[2;34m\u001b[0m\n\u001b[2;37m{(tvitaj_sxatumoj + ' ' * (12 - len(tvitaj_sxatumoj))) if tvitaj_sxatumoj != None else ''}{(tvitaj_retvitoj) if tvitaj_retvitoj != None else ''}\u001b[0m\n```"""
                    

    subteksto = "❗ + "
    bilda_kvanto = len(bildoj)
    gifbilda_kvanto = len(gifbildoj)
    videa_kvanto = len(videoj)
    subteksto += f"{bilda_kvanto} bildo{'j' if bilda_kvanto > 1 else ''}, " if bilda_kvanto > 0 else ""
    subteksto += f"{gifbilda_kvanto} gif-bildo{'j' if gifbilda_kvanto > 1 else ''}, " if gifbilda_kvanto > 0 else ""
    subteksto += f"{videa_kvanto} video{'j' if videa_kvanto > 1 else ''}, " if videa_kvanto > 0 else ""
    subteksto += f"{kvanto_de_alio} dosiero{'j' if kvanto_de_alio > 1 else ''}, " if kvanto_de_alio > 0 else ""
    subteksto = subteksto[:-2]
    if (subteksto == "❗ "): 
        subteksto = ""

    if (subteksto_responda != "" and subteksto != ""): 
        subteksto = subteksto_responda + " • " + subteksto
    else: 
        subteksto = subteksto_responda + subteksto

    #if (len(bildoj) != 0):
    #    bildo = c.kunigi(bildoj)
    #    bd_nomo = f"bildo_{kanalo.id}_{mesagxo.id}.jpg"
    #    bildo.save(bd_nomo)

    #dosiero = interactions.File(filename="bildoj/krisigno_sen_fono.png")
    subajxo = None
    if (avataro_respondata != ""):
        subajxo = interactions.EmbedFooter(
            text=subteksto,
            icon_url=avataro_respondata,
        )
    elif (subteksto != ""):
        subajxo = interactions.EmbedFooter(text=subteksto)
    
    rezulto = interactions.Embed(
        author=interactions.EmbedAuthor(
            name=nomo,
            icon_url=avataro,
        ),
        title = "⮪ La originala mesaĝo",
        url = mesagxo.url,
        description=enhavo,
        timestamp=mesagxo.timestamp,
        color=0x1EC34B,
        image=interactions.EmbedImageStruct(url=bilda_ligilo) if (bilda_ligilo != None) else None,
        video=interactions.EmbedImageStruct(url=videa_ligilo) if (videa_ligilo != None) else None,
        footer=subajxo,
    )
    return rezulto

async def ensteltabuligi(self, gilda_id: int, mesagxo: interactions.Message, por: int, kontraux: int, emogxio: interactions.Emoji, emogxio_kontrauxa: interactions.Emoji):
    kanalo = await interactions.get(
        self.client,
        interactions.Channel,
        object_id=db[f"steltabulo_{gilda_id}_kanalo"],
        parent_id=gilda_id,
    )
    mesagxkanalo = await mesagxo.get_channel()
    plusenhavo = await plusenhavo_el_mesagxo(self, mesagxo, gilda_id)
    
    steltabula_mesagxo = await kanalo.send(
        content=f"{f'<#{mesagxkanalo.parent_id}> 🢧 ' if (mesagxkanalo.type in range(10, 13)) else ''}<#{mesagxkanalo.id}>\n" \
        f"{emogxio}   **x{por}**{f'   |   {emogxio_kontrauxa}   **x{kontraux}**' if (emogxio_kontrauxa != None) else ''}\n",
        embeds=plusenhavo,
    )
    
    c.purigi(gilda_id)
    tempo = datetime.utcnow()
    for p in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_{mesagxkanalo.id}.{mesagxo.id}_"):
        del db[p]
    db[f"steltabulo_{gilda_id}_mesagxoj_{mesagxkanalo.id}.{mesagxo.id}_{round(tempo.timestamp())}"] = f"{kanalo.id}.{steltabula_mesagxo.id}"

    await mesagxo.create_reaction(emogxio)

class Steltabulo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    # KOMANDO /STELTABULO
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        #scope=GUILD
    )
    async def steltabulo(self, ctx):
        return None

    # /STELTABULO AGORDI
    @steltabulo.subcommand()
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
    )
    @interactions.option(
        description="Kiom da steloj (aŭ je kiom pli ol kontraŭsteloj) estu por ke la afiŝo ensteltabuliĝu. Defaŭlte: 4"
    )
    @interactions.option(
        description="Ĉu uzebligi kontraŭstelojn. Defaŭlte: Jes",
        choices=c.jesne,
    )
    @interactions.option(
        description="Ĉu ignori sinstelumojn (kaj sinkontraŭstelumojn). Defaŭlte: Jes",
        choices=c.jesne,
    )
    @interactions.option(
        description="Ĉu ne ensteltabuligi afiŝon, se la sendinto ĝin kontraŭstelumis. Defaŭlte: Jes",
        choices=c.jesne,
    )
    async def aktivigi(self, ctx, kanalo: interactions.Channel, kvanto: int = 4, kontrauxsteloj: int = 1, ignori_sinstelumojn: int = 1, stelblokado: int = 1):
        """Agordi la steltabulon kaj aktivigi ĝin"""
        gilda_id = ctx.guild.id
        sxlosiloj = db.keys()
        if (f"steltabulo_{gilda_id}_kanalo" not in sxlosiloj):
            if (kvanto <= 0):
                await ctx.send("""🚫 `kvanto` devas esti pozitiva nombro.""", ephemeral=True)
                return None
            if (kanalo.type != interactions.ChannelType.GUILD_TEXT):
                await ctx.send("""🚫 `kanalo` devas esti normala tekstkanalo.""", ephemeral=True)
                return None
            try:
                mesagxo = await kanalo.send("**Agordado de la kanalo kiel steltabula...**")
            except:
                await ctx.send(f"""🚫 `kanalo`=<#{kanalo.id}> ne alireblas por mi.""", ephemeral=True)
                return None
            else:
                await mesagxo.delete("Permeskontrola mesaĝo")
            teksto = \
                f"**Agordado...**\n" \
                f"> _Kanalo:_ <#{kanalo.id}>\n" \
                f"> _Minimume da steloj:_ {kvanto if not kontrauxsteloj else f'je {kvanto} pli ol da kontraŭsteloj'}\n" \
                f"> _La emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
            if (not not kontrauxsteloj):
                teksto += f"> _La kontraŭa emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
            teksto += f"\n_Ne reagumu por nuligi la agon_"
            await ctx.send(teksto)
            db[f"steltabulo_{gilda_id}_kanalo"] = str(kanalo.id)
            db[f"steltabulo_{gilda_id}_kvanto"] = str(kvanto)
            db[f"steltabulo_{gilda_id}_is_sb"] = str(ignori_sinstelumojn) + str(stelblokado)
            if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio"]
            if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
        else:
            await ctx.send("""🚫 Jam estas aktiva steltabulo. Agordu ĝin per `/steltabulo agordi` kaj `/steltabulo emogxioj`""", ephemeral=True)

    @steltabulo.subcommand()
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
    )
    @interactions.option(
        description="Kiom da steloj (aŭ je kiom pli ol kontraŭsteloj) estu por ke la afiŝo ensteltabuliĝu"
    )
    @interactions.option(
        description="Ĉu ignori sinstelumojn (kaj sinkontraŭstelumojn)",
        choices=c.jesne,
    )
    @interactions.option(
        description="Ĉu ne ensteltabuligi afiŝon, se la sendinto ĝin kontraŭstelumis",
        choices=c.jesne,
    )
    async def agordi(self, ctx, kanalo: interactions.Channel = None, kvanto: int = None, ignori_sinstelumojn: int = None, stelblokado: int = None):
        """Reagordi la steltabulon kaj vidi ĝiajn agordojn"""
        gilda_id = ctx.guild.id
        sxlosiloj = db.keys()
        kanala_id = 0
        if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj):
            if (kvanto != None and kvanto <= 0):
                await ctx.send("""🚫 `kvanto` devas esti pozitiva nombro.""", ephemeral=True)
                return None            
            if (kanalo != None and kanalo.type != interactions.ChannelType.GUILD_TEXT):
                await ctx.send("""🚫 `kanalo` devas esti normala tekstkanalo.""", ephemeral=True)
                return None
            if (kanalo != None):
                try:
                    mesagxo = await kanalo.send("**Agordado de la kanalo kiel steltabula...**")
                except:
                    await ctx.send(f"""🚫 `kanalo`=<#{kanalo.id}> ne alireblas por mi.""", ephemeral=True)
                    return None
                else:
                    await mesagxo.delete("Permeskontrola mesaĝo")
                    kanala_id = kanalo.id
                    db[f"steltabulo_{gilda_id}_kanalo"] = str(kanala_id)
            else:
                kanala_id = db[f"steltabulo_{gilda_id}_kanalo"]
            kv = kvanto
            if (kv == None): kv = db[f"steltabulo_{gilda_id}_kvanto"]
            is_sb = str(ignori_sinstelumojn) if (ignori_sinstelumojn != None) else db[f"steltabulo_{gilda_id}_is_sb"][0]
            is_sb += str(stelblokado) if (stelblokado != None) else db[f"steltabulo_{gilda_id}_is_sb"][1]
            db[f"steltabulo_{gilda_id}_kvanto"] = str(kv)
            db[f"steltabulo_{gilda_id}_is_sb"] = str(is_sb)
            teksto = \
                f"**La steltabulaj agordoj:**\n" \
                f"> _Kanalo:_ <#{kanala_id}>\n" \
                f"> _Minimume da steloj:_ {kv if f'steltabulo_{gilda_id}_emogxio_kontrauxa' not in sxlosiloj else f'je {kv} pli ol da kontraŭsteloj'}\n" \
                f"> _Sinstelumoj {'ne ' if is_sb[0]=='1' else ''}enkalkuliĝas_\n" \
                f"> _Sinkontraŭstelumoj {'ne nepre ' if is_sb[1]=='0' else ''}malpermesas ensteltabuligon_\n"
            await ctx.send(teksto)
        else:
            await ctx.send("""🚫 Ankoraŭ ne estas aktiva steltabulo. Aktivigu ĝin per `/steltabulo aktivigi`""", ephemeral=True)

    @steltabulo.subcommand()
    async def emogxioj(self, ctx):
        """Reelekti la emoĝiojn por steltabulo. La jamaj steltabulaj mesaĝoj ne plu sinĥroniĝos!"""
        gilda_id = ctx.guild.id
        sxlosiloj = db.keys()
        if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj):
            del db[f"steltabulo_{gilda_id}_emogxio"]
            teksto = \
                "**Steltabulaj emoĝioj:**\n" \
                "> _La pora emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
            if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj):
                del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
                teksto += "> _La kontraŭa emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
            for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
                del db[e]
            await ctx.send(teksto)
        else:
            await ctx.send("""🚫 Ankoraŭ ne estas aktiva steltabulo. Aktivigu ĝin per `/steltabulo aktivigi`""", ephemeral=True)

    @steltabulo.subcommand()
    async def malaktivigi(self, ctx):
        """Malaktivigi la steltabulon. La agordoj malaperos! La jamaj steltabulaj mesaĝoj ne plu sinĥroniĝos!"""
        gilda_id = ctx.guild.id
        sxlosiloj = db.keys()
        if (f"steltabulo_{gilda_id}_kanalo" in sxlosiloj): 
            del db[f"steltabulo_{gilda_id}_kanalo"]
            if (f"steltabulo_{gilda_id}_kvanto" in sxlosiloj): del db[f"steltabulo_{gilda_id}_kvanto"]
            if (f"steltabulo_{gilda_id}_is_sb" in sxlosiloj): del db[f"steltabulo_{gilda_id}_is_sb"]
            if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio"]
            if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
            for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
                del db[e]
            await ctx.send("**La steltabulo malaktiviĝis**")
        else:
            await ctx.send("**La steltabulo jam estas malaktiva**")

    # PRITRAKTADO DE ALDONOJ DE REAGUMOJ
    @interactions.extension_listener()
    async def on_message_reaction_add(self, reagumo: interactions.MessageReaction):
        steltabulaj_sxlosiloj = db.prefix("steltabulo_")
        gilda_id = reagumo.guild_id
        mesagxo = await interactions.get(
            self.client,
            interactions.Message,
            object_id=reagumo.message_id,
            parent_id=reagumo.channel_id,
            force="http"
        )
        if (f"steltabulo_{gilda_id}_kanalo" in steltabulaj_sxlosiloj and reagumo.user_id != ID):
            teksto = mesagxo.content
            if ((mesagxo.author.id == ID) and (teksto[:15] == "**Agordado...**" or teksto[:24] == "**Steltabulaj emoĝioj:**") and (mesagxo.interaction.user.id == reagumo.user_id)):
                teksto = re.sub(r"`Neniu, bonvolu reagumi per la taŭga emoĝio`", str(reagumo.emoji), teksto, 1)
                if (f"steltabulo_{str(gilda_id)}_emogxio" not in steltabulaj_sxlosiloj):
                    db[f"steltabulo_{str(gilda_id)}_emogxio"] = f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
                    if (re.search(r"_La kontraŭa emoĝio:_", teksto) == None):
                        for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
                            del db[e]
                        teksto = re.sub(r"\*+Agordado\.+\*+", "**Sukcese agordite**", teksto)
                elif (re.search(r"_La kontraŭa emoĝio:_", teksto) != None and f"steltabulo_{str(gilda_id)}_emogxio_kontrauxa" not in steltabulaj_sxlosiloj):
                    db[f"steltabulo_{str(gilda_id)}_emogxio_kontrauxa"] = f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
                    for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
                        del db[e]
                    teksto = re.sub(r"\*+Agordado\.+\*+", "**Sukcese agordite**", teksto)
                await mesagxo.edit(teksto)

            elif (f"steltabulo_{gilda_id}_emogxio" in steltabulaj_sxlosiloj):
                is_sb = db[f"steltabulo_{gilda_id}_is_sb"]
                e_id = db[f"steltabulo_{gilda_id}_emogxio"]
                emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)
                emogxio_kontrauxa = None
                if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in steltabulaj_sxlosiloj):
                    ek_id = db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
                    emogxio_kontrauxa = await c.emogxio_el_datumbazo(self, gilda_id, ek_id)
                if (str(reagumo.emoji) == str(emogxio) or str(reagumo.emoji) == str(emogxio_kontrauxa)):
                    kvanto_pora = c.reaguma_kvanto(mesagxo, emogxio)
                    kvanto_kontrauxa = c.reaguma_kvanto(mesagxo, emogxio_kontrauxa)
                    if (is_sb != '00' and emogxio_kontrauxa != None):
                        reagumintoj = await mesagxo.get_users_from_reaction(emogxio_kontrauxa)
                        identigiloj = [u.id for u in reagumintoj]
                        if (mesagxo.author.id in identigiloj):
                            kvanto_kontrauxa = (kvanto_pora if (is_sb[1] == '1') else kvanto_kontrauxa-1)
                    reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
                    identigiloj = [u.id for u in reagumintoj]
                    if (is_sb[0] == '1' and mesagxo.author.id in identigiloj):
                        kvanto_pora -= 1

                    if (kvanto_pora-kvanto_kontrauxa >= int(db[f"steltabulo_{gilda_id}_kvanto"]) and ID not in identigiloj):

                        await ensteltabuligi(self, gilda_id, mesagxo, kvanto_pora, kvanto_kontrauxa, emogxio, emogxio_kontrauxa)

                    else:
                        await c.gxisdatigi(self, gilda_id, reagumo.channel_id, reagumo.message_id)

    @interactions.extension_listener()
    async def on_message_reaction_remove(self, reagumo: interactions.MessageReaction):

        steltabulaj_sxlosiloj = db.prefix("steltabulo_")
        gilda_id = reagumo.guild_id
        mesagxo = await interactions.get(
            self.client,
            interactions.Message,
            object_id=reagumo.message_id,
            parent_id=reagumo.channel_id,
            force="http"
        )
        if (f"steltabulo_{gilda_id}_emogxio" in steltabulaj_sxlosiloj):
            e_id = db[f"steltabulo_{gilda_id}_emogxio"]
            emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)
            emogxio_kontrauxa = None
            if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in steltabulaj_sxlosiloj):
                ek_id = db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
                emogxio_kontrauxa = await c.emogxio_el_datumbazo(self, gilda_id, ek_id)
            if (str(reagumo.emoji) == str(emogxio) or str(reagumo.emoji) == str(emogxio_kontrauxa)):
                kvanto_pora = c.reaguma_kvanto(mesagxo, emogxio)
                kvanto_kontrauxa = c.reaguma_kvanto(mesagxo, emogxio_kontrauxa)
                reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
                identigiloj = [u.id for u in reagumintoj]
    
                if (kvanto_pora-kvanto_kontrauxa >= int(db[f"steltabulo_{gilda_id}_kvanto"]) and ID not in identigiloj):
    
                    await ensteltabuligi(self, gilda_id, mesagxo, kvanto_pora, kvanto_kontrauxa, emogxio, emogxio_kontrauxa)
    
                else:
                    await c.gxisdatigi(self, gilda_id, reagumo.channel_id, reagumo.message_id)


def setup(client):
    Steltabulo(client)
