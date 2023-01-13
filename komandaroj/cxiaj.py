from replit import db
import interactions as i


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
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        for r in listo:
            if (str(r.emoji) == str(emogxio)): nombro = r.count
    return nombro
