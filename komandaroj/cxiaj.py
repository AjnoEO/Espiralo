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
                if (str(r.emoji) == str(emogxio)): 
                    nombro = r.count
                    break
        elif (emogxio[0] == 'i'):
            for r in listo:
                if (int(r.emoji.id) == int(emogxio[1:])): 
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
            r"(" + re.escape(f"{emogxio}") + r"[\s*x]+)(\d+)(\*\*)",
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
                r"(" + re.escape(f"{emogxio}") + r"[\s*x]+)(\d+)(\*\*)",
                r"\g<1>" + re.escape(str(kvanto)) + r"\3", 
                teksto
            )
        await mesagxo.edit(content = teksto)