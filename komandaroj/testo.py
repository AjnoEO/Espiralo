import interactions
import os
from replit import db

GUILD = os.environ['GUILD_ID']

class Testo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.lasta_forigmesagxo = None
        self.forigprefikso = None

    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD
    )
    async def testo(self, ctx):
        return None

    @testo.subcommand()
    @interactions.option(
        str,
        name="opcio",
        description="Testa opcio",
        autocomplete=True,
    )
    async def testa(self, ctx, opcio: str):
        """Testa komando"""
        await ctx.send(
            f"{opcio}\n" \
            f"Longo: {len(opcio)}" \
        )

    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD,
    )
    async def datumbazo(self, ctx): #database
        return None
    
    @datumbazo.subcommand()
    async def listigi(self, ctx):
        """Montri la enhavon de la datumbazo""" #show the contents of the database
        s = "Jen la enhavo de la datumbazo:\n" #"here are the contents of the database:\n"
        for sxlosilo in db.keys():
            s += f"`{sxlosilo}`: `{db[sxlosilo]}`\n" #"[key]: [value]"
        await ctx.send(s)

    @datumbazo.subcommand()
    @interactions.option(
        description = "La anstataŭigenda signovico", #the string to be replaced
        required = True,
    )
    @interactions.option(
        description = "La anstataŭonta signovico", #the string to replace with
        required = True,
    )
    async def anstatauxigi(self, ctx, kion: str, per_kio: str): #replace in keys
        """Anstataŭigi signovicojn en la datumbazo"""
        k = 0
        p = 0
        sxlosilaro = db.keys()
        for sxlosilo in sxlosilaro:
            if kion in sxlosilo:
                s = sxlosilo.replace(kion, per_kio)
                if s in sxlosilaro: 
                    p += 1
                else:
                    k += 1
                    db[s] = db[sxlosilo]
                    del db[sxlosilo]
        plk = "j" if k != 1 else ""
        plp = "j" if k != 1 else ""
        await ctx.send(
            f"Farite\n" \
            f"Ŝlosilo{plk} de {k} elemento{plk} estis renomita{plk}\n"  \
            f"{f'{p} ŝlosilo{plp} ne renomeblis pro ekzisto de aliaj samnomaj ŝlosiloj' if p > 0 else ''}"
        )

    @datumbazo.subcommand()
    @interactions.option(
        description = "La prefikso de la forigendaj ŝlosiloj",
        required = True,
    )
    async def forigi(self, ctx, kion: str):
        """Forigi elementojn, kies ŝlosiloj komenciĝas je certa prefikso"""
        k = 0
        s = ""
        sxlosilaro = db.prefix(kion)
        for sxlosilo in sxlosilaro:
            s += f"`{sxlosilo}`: `{db[sxlosilo]}`\n"
            k += 1
        if k == 0:
            await ctx.send(f"Jam mankas ŝlosiloj kun la prefikso `{kion}`")
        else:
            b = interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                label="Jes, forigi",
                custom_id="forigi_el_datumbazo"
            )
            plk = "j" if k > 1 else ""
            s = f"Vi volas forigi el la datumbazo {k} elemento{plk}n:\n{s}"
            self.forigprefikso = kion
            if self.lasta_forigmesagxo != None:
                await self.lasta_forigmesagxo.disable_all_components()
            self.lasta_forigmesagxo = await ctx.send(s, components=b)

    @interactions.extension_component("forigi_el_datumbazo")
    async def forigi_el_datumbazo(self, ctx):
        print(dir(self.lasta_forigmesagxo))
        for sxlosilo in db.prefix(self.forigprefikso):
            del db[sxlosilo]
        await self.lasta_forigmesagxo.disable_all_components()
        await ctx.send("La elementoj foriĝis")
    
    @interactions.extension_autocomplete("testo", "opcio")
    async def testo_autocomplete(self, ctx, value = ""):
        koloroj = ["bluo", "verdo", "flavo", "ruĝo", "blanko", "nigro"]
        elektoj = [interactions.Choice(name = koloro, value = koloro) for koloro in koloroj if value in koloro]
        await ctx.populate(elektoj)

def setup(client):
    Testo(client)