from replit import db
import interactions as i

def lingvonomo(nomo: str, plena: bool = True, ekmajuskle: bool = False, akuzative: bool = False):
    ak = "n" if akuzative else ""
    if (nomo[len(nomo)-1]=='a'):
        return f"{'L' if ekmajuskle else 'l'}a " + nomo + ak + ((" lingvo" + ak) if plena else "")
    else:
        return nomo.capitalize() + ak

def sxlosilo_el_valoro(self, valoro: str, prefikso: str = ""):
    for s in db.keys():
        if (db[s] == valoro):
            return s
    return None

def reaguma_kvanto(mesagxo: i.Message, emogxia_nomo: str):
    listo = mesagxo.reactions
    nombro = 0
    if (listo != None):
        for r in listo:
            if (r.emoji.name == emogxia_nomo): nombro = r.count
    return nombro

#def rolmenuo(rolaro, )