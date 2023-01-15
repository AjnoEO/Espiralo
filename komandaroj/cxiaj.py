from replit import db
import interactions as i
from PIL import Image
import requests
import re

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


def reaguma_kvanto(mesagxo: i.Message, emogxio: i.Emoji):
    """Kvanto de la reagumoj per `emogxio` sub `mesagxo`"""
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        for r in listo:
            if (str(r.emoji) == str(emogxio)): nombro = r.count
    return nombro

def kunigi(bildoj: list):
    """Bildo enhavanta ĉiujn bildojn el la listo `bildoj`, kolumne"""
    w = 0
    h = 0
    for b in bildoj:
        print(f"W: {b.width}")
        if (w < b.width): w = b.width
    heights = {b: b.height*w/(b.width) for b in bildoj}
    for b in bildoj:
        h = h + heights[b]
    print(f"{w}x{h} por {len(bildoj)} bildo{'j' if len(bildoj)>1 else ''}")
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