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

#def rolmenuo(rolaro, )