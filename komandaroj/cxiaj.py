import os
from replit import db
import interactions as i
from PIL import Image
import requests
import re
from datetime import datetime

USERNAME = os.environ['USERNAME_DISCRIMINATOR']

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

async def reaguma_kvanto(mesagxo: i.Message, emogxio: i.Emoji, sen_roboto: bool = False):
    """Kvanto de la reagumoj per `emogxio` sub `mesagxo` (eksklude la roboton se `sen_roboto`)"""
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        for r in listo:
            if (str(r.emoji) == str(emogxio)): nombro = r.count
    reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
    uzantnomoj = [f"{u.username}#{u.discriminator}" for u in reagumintoj]
    if USERNAME in uzantnomoj:
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

def atentendaj(gilda_id: int):
    """Listo de la mesaĝoj, kiujn necesas atenti por la steltabulo en la gildo kun la ID `gilda_id`"""
    if (f"steltabulo_{gilda_id}_atentendaj" in db.prefix("steltabulo_")):
        teksto = db[f"steltabulo_{gilda_id}_atentendaj"]
        listo = re.findall(r"|([0-9.,]+):([0-9]+\.[0-9]+):([0-9]+)\.([0-9]+)", teksto)
        nuno = datetime.utcnow()
        listo_nova = listo
        teksto_nova = ""
        for e in listo:
            if e[0] != '':
                tiamo = datetime.utcfromtimestamp(float(e[0]))
                if ((nuno - tiamo).days <= 30):
                    teksto_nova += f"|{e[0]}:{e[1]}:{e[2]}.{e[3]}"
        db[f"steltabulo_{gilda_id}_atentendaj"] = teksto_nova
        listo = re.findall(r"|([0-9.,]+):([0-9]+)\.([0-9]+):([0-9]+)\.([0-9]+)", teksto_nova)
        return listo_nova
    else:
        return None

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

def steltabula_mesagxo(gilda_id: int, kanala_id: int, mesagxa_id: int):
    """Paro (`kanalo`, `mesagxo`) de la steltabula mesaĝo de la roboto, kie ĝi montris la mesaĝon `mesagxa_id` el `kanala_id`"""
    listo = atentendaj(gilda_id)
    id = f"{kanala_id}.{mesagxa_id}"
    for e in listo:
        if (id == e[1]):
            return (int(e[2]), int(e[3]))
    return None
    #|{datetime.timestamp}:{channel_id}.{message_id}:{starboard_channel}.{starboard_message}|