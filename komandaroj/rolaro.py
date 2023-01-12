import interactions
import os
from replit import db

GUILD = os.environ['GUILD_ID']

    
class Rolaro(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
    
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD,
    )
    async def rolaro(self, ctx):
        return None

    @rolaro.subcommand()
    @interactions.option(
        name="nomo", 
        description="Nomo de la rolaro", 
        required=True
    )
    @interactions.option(
        name="limigiteco",
        description="Ĉu elekteblu nur unu el la roloj (defaŭlte ne)",
        choices=[
            interactions.Choice(
                name="Jes",
                value=1
            ),
            interactions.Choice(
                name="Ne",
                value=0
            ),
        ],
        required=False,
    )
    async def krei(self, ctx, nomo: str = "", limigiteco: int = 0):
        """Krei rolaron"""
        if f"rolaro_{ctx.guild.id}_{nomo}" in db.prefix("rolaro_"):
            await ctx.send(f"La rolaro `{nomo}` jam troveblas en la datumbazo")
        else:
            db[f"rolaro_{ctx.guild.id}_{nomo}"] = str(limigiteco)
            await ctx.send(f"La rolaro `{nomo}` kreiĝis")

    @rolaro.subcommand()
    @interactions.option(
        name="nomo", 
        description="Nomo de la rolaro",
        autocomplete=True,
        required=True,
    )
    @interactions.option(
        name="rolo", 
        description="Rolo aldonenda en la rolaron", 
        required=True
    )
    async def aldoni(self, ctx, nomo: str, rolo: interactions.Role):
        """Aldoni rolon en rolaron"""
        if f"rolaro_{ctx.guild.id}_{nomo}" in db.prefix("rolaro_"):
            rlrj = db.prefix(f"rolaro_{ctx.guild.id}_")
            jam = False
            for it in rlrj:
                if ("|" + str(rolo.id) in db[it]) and not jam:
                    jam = True
                    if it == f"rolaro_{ctx.guild.id}_{nomo}": await ctx.send(f"La rolo `{rolo.name}` jam estas en ĉi tiu rolaro")
                    else: await ctx.send(f"La rolo `{rolo.name}` jam estas en la rolaro `{it[len(f'rolaro_{ctx.guild.id}_'):]}`")
            if not jam:
                db[f"rolaro_{ctx.guild.id}_{nomo}"] += "|" + str(rolo.id)
                await ctx.send(f"La rolo `{rolo.name}` aldoniĝis en la rolaron `{nomo}`")
        else:
            await ctx.send(f"La rolaro `{nomo}` ne troveblas en la datumbazo")

    @rolaro.subcommand()
    @interactions.option(
        name="nomo", 
        description="Nomo de la rolaro",
        autocomplete=True,
        required=True,
    )
    @interactions.option(
        name="rolo", 
        description="Rolo eligenda el la rolaro", 
        required=True
    )
    async def eligi(self, ctx, nomo: str, rolo: interactions.Role):
        """Eligi rolon el rolaro"""
        if f"rolaro_{ctx.guild.id}_{nomo}" in db.prefix("rolaro_"):
            s = db[f"rolaro_{ctx.guild.id}_{nomo}"]
            if ("|" + str(rolo.id) in s):
                n = s.find("|" + str(rolo.id))
                l = len("|" + str(rolo.id))
                db[f"rolaro_{ctx.guild.id}_{nomo}"] = s[:n-1] + s[n+l:]
                await ctx.send(f"La rolo `{rolo.name}` eliĝis el la rolaro `{nomo}`")
            else:
                await ctx.send(f"La rolo `{rolo.name}` jam mankas en ĉi tiu rolaro")
        else:
            await ctx.send(f"La rolaro `{nomo}` ne troveblas en la datumbazo")

    @rolaro.subcommand()
    @interactions.option(
        name="nomo",
        description="Nomo de la rolaro",
        autocomplete=True,
        required=True,
    )
    async def forigi(self, ctx, nomo: str):
        """Forigi rolaron"""
        if f"rolaro_{ctx.guild.id}_{nomo}" in db.prefix("rolaro_"):
            del db[f"rolaro_{ctx.guild.id}_{nomo}"]
            await ctx.send(f"La rolaro `{nomo}` foriĝis el la datumbazo")
        else:
            await ctx.send(f"La rolaro `{nomo}` ne  en la datumbazo")

#    @rolaro.subcommand()
#    @interactions.option(
#        name="kion",
#        description="Kiun rolaron importi",
#        choices=[
#            interactions.Choice(
#                name="Lingvoj",
#                value=0,
#            ),
#            interactions.Choice(
#                name="Lingvoj denaskaj k lingvoj lernataj",
#                value=1,
#            )
#        ]
#    )
#    async def importi(self, ctx, kion: int):
#        """Importi rolarojn kreatajn de la robotestro"""
#        if kion == 0:
#            if 
    
    @interactions.extension_autocomplete("rolaro", "nomo")
    async def nomo_autocomplete(self, ctx, value = ""):
        self.rolaro = value
        gildo = ctx.guild.id
        ind = len(f"rolaro_{gildo}_")
        rolaroj = db.prefix(f"rolaro_{gildo}_")
        elektejo = [
            interactions.Choice(name = sxlosilo[ind:], value = sxlosilo[ind:]) 
            for sxlosilo in rolaroj 
            if value in sxlosilo
        ]
        await ctx.populate(elektejo)
    
def setup(client):
    Rolaro(client)