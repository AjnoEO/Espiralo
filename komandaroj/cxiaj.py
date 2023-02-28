import os
from replit import db
import interactions as i
from PIL import Image
import requests
import re
from datetime import datetime, timedelta

jesne = [
    i.Choice(
        name="Jes",
        value=1
    ),
    i.Choice(
        name="Ne",
        value=0
    ),
]

async def plusenhavo_el_mesagxo(self, mesagxo: i.Message, gilda_id: int):
    """Plusenhavo (interaction.Embed) reprezentanta la mesaĝon `mesagxo`"""
    ano = None
    avataro = ""
    nomo = ""
    try:
        ano = await i.get(
            self.client,
            i.Member,
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
    if (mesagxo.type == i.MessageType.REPLY and (mesagxo.message_reference.fail_if_not_exists != True)):
        #rjsono = mesagxo._json["referenced_message"]
        mesagxo_respondata = await i.get(
            self.client,
            i.Message,
            object_id=mesagxo.message_reference.message_id,
            parent_id=mesagxo.message_reference.channel_id,
            force="http"
        )
        ano_respondata = await i.get(
            self.client,
            i.Member,
            object_id=mesagxo_respondata.author.id,
            parent_id=gilda_id
        )
        avataro_respondata = ano_respondata.get_avatar_url(gilda_id)
        if (avataro_respondata == None):
            avataro_respondata = mesagxo_respondata.author.avatar_url
        nomo_respondata = ano_respondata.nick
        if (nomo_respondata == None):
            nomo_respondata = mesagxo_respondata.author.username
        if mesagxo_respondata.author.bot:
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

    #dosiero = i.File(filename="bildoj/krisigno_sen_fono.png")
    subajxo = None
    if (avataro_respondata != ""):
        subajxo = i.EmbedFooter(
            text=subteksto,
            icon_url=avataro_respondata,
        )
    elif (subteksto != ""):
        subajxo = i.EmbedFooter(text=subteksto)
    
    rezulto = i.Embed(
        author=i.EmbedAuthor(
            name=nomo,
            icon_url=avataro,
        ),
        title = "⮪ La originala mesaĝo",
        url = mesagxo.url,
        description=enhavo,
        timestamp=mesagxo.timestamp,
        color=0x1EC34B,
        image=i.EmbedImageStruct(url=bilda_ligilo) if (bilda_ligilo != None) else None,
        video=i.EmbedImageStruct(url=videa_ligilo) if (videa_ligilo != None) else None,
        footer=subajxo,
    )
    return rezulto

def sxlosilo_el_valoro(self, valoro: str, prefikso: str = ""):
    for s in db.keys():
        if (db[s] == valoro):
            return s
    return None

def EKS_reaguma_kvanto(mesagxo: i.Message, emogxia_nomo: str):
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        for r in listo:
            if (r.emoji.name == emogxia_nomo): nombro = r.count
    return nombro

def reaguma_kvanto(mesagxo: i.Message, emogxio, sen_roboto: bool = False):
    """Kvanto de la reagumoj per `emogxio` sub `mesagxo` (eksklude la roboton se `sen_roboto`)"""
    if (emogxio == None):
        return 0
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        if (type(emogxio) is i.Emoji):
            for r in listo:
                if (r.emoji.format == emogxio.format): 
                    nombro = r.count
                    break
        elif (emogxio[0] == 'i'):
            for r in listo:
                if (r.emoji.id == int(emogxio[1:])): 
                    nombro = r.count
                    break
        else:
            for r in listo:
                if (str(r.emoji.name) == str(emogxio[1:])): 
                    nombro = r.count
                    break
    if sen_roboto:
        nombro -= 1
    return nombro

def kunigi(bildoj: list):
    """Bildo enhavanta ĉiujn bildojn el la listo `bildoj`, kolumne"""
    w = 0
    h = 0
    for b in bildoj:
        if (w < b.width): w = b.width
    heights = {b: b.height*w/(b.width) for b in bildoj}
    for b in bildoj:
        h = h + heights[b]
    rez = Image.new("RGB", (w, h))
    h = 0
    for b in bildoj:
        rez.paste(b.resize( (w, heights[b])), (0, h) )
        h = h + heights[b]
    return rez

def tenora_gifo(ligilo: str):
    """La ligilo al la gifo, trovebla per nomala ligilo `ligilo`"""
    pagxo = requests.get(ligilo).text
    regespo = r"(?i)\b((https?://media[.]tenor[.]com/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))[.]gif)"
    return re.findall(regespo, pagxo)[0][0]

def purigi(gilda_id: int, nova_mesagxo = None):
    tempo = datetime.utcnow() - timedelta(days=30)
    tempo = round(tempo.timestamp())
    for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
        r = re.split(r"_", e)
        if (int(r[-1]) < tempo):
            del db[e]
    return 0

async def emogxio_el_datumbazo(self, gilda_id: int, emogxio: str):
    """Emogxia objekto (interactions.Emoji) el la datumbaza signovico `emogxio`"""
    if (emogxio[0] == 'i'):
        rez = await i.get(
            self.client,
            i.Emoji,
            object_id=emogxio[1:],
            parent_id=gilda_id
        )
    else:
        rez = i.Emoji(name=emogxio[1:])
    return rez



async def gxisdatigi(self, gilda_id: int, kanala_id: int, mesagxa_id: int):
    m = db.prefix(f"steltabulo_{gilda_id}_mesagxoj_{kanala_id}.{mesagxa_id}_")
    if (m != None and len(m) > 0):
        purigi(gilda_id)
        m = m[0]
        r = re.findall(r"(\d+)", db[m])
        mesagxo = await i.get(
            self.client,
            i.Message,
            object_id=int(r[1]),
            parent_id=int(r[0]),
            force="http",
        )
        originala = await i.get(
            self.client,
            i.Message,
            object_id=mesagxa_id,
            parent_id=kanala_id,
            force="http",
        ) 
        emogxio = await emogxio_el_datumbazo(
            self, 
            gilda_id,
            db[f"steltabulo_{gilda_id}_emogxio"]
        )
        kvanto = reaguma_kvanto(
            originala,
            emogxio,
            sen_roboto=True
        )
        teksto = mesagxo.content
        teksto = re.sub(
            r"(" + re.escape(f"{emogxio.format}") + r"[\s*x]+)(\d+)(\*\*)",
            r"\g<1>" + re.escape(str(kvanto)) + r"\3", 
            teksto
        )
        if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in db.prefix("steltabulo_")):
            emogxio = await emogxio_el_datumbazo(
                self, 
                gilda_id,
                db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
            )
            kvanto = reaguma_kvanto(
                originala,
                emogxio
            )
            teksto = re.sub(
                r"(" + re.escape(f"{emogxio.format}") + r"[\s*x]+)(\d+)(\*\*)",
                r"\g<1>" + re.escape(str(kvanto)) + r"\3", 
                teksto
            )
        await mesagxo.edit(content = teksto)