import interactions
import os
from replit import db
from kogoj.cxiaj import lingvonomo
from kogoj.cxiaj import sxlosilo_el_valoro

GUILD = os.environ['GUILD_ID']

class Lingvo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    def enas(self, gilda_id, idoj):
        if idoj == []:
            return False
        for sxlosilo in db.prefix(f"ling_rol_den_{gilda_id}"):
            if db[sxlosilo] in idoj:
                return True
        for sxlosilo in db.prefix(f"ling_rol_lern_{gilda_id}"):
            if db[sxlosilo] in idoj:
                return True
        return False
    
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD,
    )
    async def lingvo(self, ctx):
        return None

    @lingvo.subcommand()
    @interactions.option(
        description="Kodo de la lingvo laŭ ISO 639-3",
        required=True,
    )
    @interactions.option(
        description="Nomo de la lingvo en Esperanto (nur adjektivo aŭ nur substantivo)",
        required=True,
    )
    @interactions.option(
        description="Rolo destinita por denaskuloj de la lingvo",
        required=False,
    )
    @interactions.option(
        description="Rolo destinita por lernantoj de la lingvo",
        required=False,
    )
    async def agordi(self, ctx, kodo: str = "", nomo: str = "", rolo_denaske: interactions.Role = None, rolo_lernate: interactions.Role = None):
        """Aldoni la lingvon al la datumbazo kaj agordi la rolojn"""
        ctx.defer()
        keys_nom = db.prefix("ling_nom_")
        testlisto = []
        if rolo_denaske != None: testlisto.append(rolo_denaske.id)
        if rolo_lernate != None: testlisto.append(rolo_lernate.id)
        if f"ling_nom_{kodo}" in keys_nom:
            await ctx.send(f"La kodo jam troveblas en la datumbazo:\n> `{kodo}`: `{db[f'ling_nom_{kodo}']}`", ephemeral=True)
        elif self.enas(ctx.guild.id, testlisto):
            lingvokodo = sxlosilo_el_valoro(str(rolo_denaske.id), "ling_rol_").split('_').last()
            rolnomo1 = (await interactions.get(self.client, interactions.Role,
                parent_id=int(ctx.guild.id),
                object_id=db[f"ling_rol_den_{int(ctx.guild.id)}_{lingvokodo}"]
            )).mention
            rolnomo2 = (await interactions.get(self.client, interactions.Role, 
                parent_id=int(ctx.guild.id),
                object_id=db[f"ling_rol_lern_{int(ctx.guild.id)}_{lingvokodo}"]
            )).mention 
            await ctx.send(f"""La rolo jam uziĝas por iu lingvo:
            > `{lingvokodo}` ({lingvonomo(db[f'ling_nom_{lingvokodo}'], plena = False)}), roloj: {rolnomo1}, {rolnomo2}""", ephemeral=True)
        else:
            db[f"ling_nom_{kodo}"] = nomo
            if rolo_denaske != None: db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"] = str(rolo_denaske.id)
            if rolo_lernate != None: db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"] = str(rolo_lernate.id)
            await ctx.send(f"{lingvonomo(nomo, ekmajuskle = True)} (`{kodo}`) aldoniĝis al la datumbazo")

    @lingvo.subcommand()
    @interactions.option(
        name="kodo",
        description="Kodo de la lingvo laŭ ISO 639-3",
        autocomplete=True,
        required=True,
    )
    async def informoj(self, ctx, kodo: str = ""):
        """Informo pri la lingvo laŭ la kodo"""
        ctx.defer()
        keys_nom = db.prefix("ling_nom_")
        if f"ling_nom_{kodo}" in keys_nom:
            sxlosiloj = db.prefix("ling_rol_")
            drolo = (await interactions.get(self.client, interactions.Role,
                parent_id=int(ctx.guild.id),
                object_id=db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"]
            )).mention if f"ling_rol_den_{int(ctx.guild.id)}_{kodo}" in sxlosiloj else "`Ne agordite`"
            lrolo = (await interactions.get(self.client, interactions.Role, 
                parent_id=int(ctx.guild.id),
                object_id=db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"]
            )).mention if f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}" in sxlosiloj else "`Ne agordite`"
            await ctx.send(
                f"""> Lingvokodo: `{kodo}`
                > Nomo de la lingvo: `{db[f'ling_nom_{kodo}']}`
                > Denaskula rolo: {drolo}
                > Lernantula rolo: {lrolo}"""
            )
        else:
            await ctx.send(f"La kodo `{kodo}` ne troveblas en la datumbazo")

    @lingvo.subcommand()
    async def listigi(self, ctx):
        """Listigi la lingvojn el la datumbazo"""
        fin = "Jen ĉiuj lingvoj en la datumbazo:\n"
        keys_nom = db.prefix("ling_nom_")
        for l in keys_nom:
            fin += f"> `{l[9:]}` ({lingvonomo(db[l], plena = False)})\n"
        await ctx.send(fin)

    @lingvo.subcommand()
    @interactions.option(
        description="Elektilo por kiaj roloj aperigendas",
        choices=[
            interactions.Choice(
                name="Denaskulaj",
                value="den",
            ),
            interactions.Choice(
                name="Lernantulaj",
                value="lern",
            )
        ],
        required=True,
    )
    @interactions.option(
        description="Kiom da lingvoj maksimume estu elekteblaj",
        required=False,
    )
    async def rolelektilo(self, ctx, tipo: str = "den", maksimumo: int = 1):
        """Krei rolelektilon por lingvaj roloj"""
        s = f"ling_rol_{tipo}_{str(ctx.guild.id)}_"
        elektilo = interactions.SelectMenu(
            options = [
                interactions.SelectOption(
                    label = lingvonomo(db[f"ling_nom_{kodo[len(s):]}"], plena = False),
                    value = kodo[len(s):],
                    description = f"Elektu se vi parolas{' aŭ lernas' if tipo == 'lern' else ''} {lingvonomo(db[f'ling_nom_{kodo[len(s):]}'], akuzative = True)}{' denaske' if tipo == 'den' else ''}",
                ) for kodo in db.prefix(s)
            ],
            placeholder = f"Elektu {'vian denaskan lingvon' if tipo == 'den' else 'la lingvojn kiujn vi parolas'}",
            custom_id = f"rolel_{tipo}",
            max_values = maksimumo,
            min_values = 0,
        )
        await ctx.send("", components=elektilo)

    @interactions.extension_component("rolel_den")
    async def rolel_den(self, ctx, value):
        ctx.defer()
        prefikso = f"ling_rol_den_{str(ctx.guild.id)}_"
        aldon = False
        forig = False
        roloj = ctx.author.roles
        for indekso in db.prefix(prefikso):
            kodo = indekso[len(prefikso):]
            if kodo in value and int(db[prefikso+kodo]) not in roloj:
                rolo = await interactions.get(
                    self.client,
                    interactions.Role,
                    parent_id=ctx.guild_id,
                    object_id=db[prefikso+kodo],
                )
                await ctx.author.add_role(rolo, guild_id=ctx.guild_id, reason="Elekto en rolelektilo")
                aldon = True
            elif kodo not in value and int(db[prefikso+kodo]) in roloj:
                rolo = await interactions.get(
                    self.client,
                    interactions.Role,
                    parent_id=ctx.guild_id,
                    object_id=db[prefikso+kodo],
                )
                await ctx.author.remove_role(rolo, guild_id=ctx.guild_id, reason="Elekto en rolelektilo")
                forig = True
        r = ""
        c = 0
        if aldon:
            r = f"Vi nun havas la rolo{'j' if len(value) > 1 else ''}n kiel denaskulo de"
            for i in range(0, len(value)):
                if i == len(value)-1 and len(value) >= 2: r += " kaj"
                elif i > 0: r += ","
                r += " " + lingvonomo(db[f'ling_nom_{value[i]}'])
        elif forig:
            if len(value) == 0: r = f"Vi ne plu havas denaskulajn rolojn"
            else:
                r += f"Vi nun havas la rolo{'j' if len(value) > 1 else ''}n kiel denaskulo de"
                for i in range(0, len(value)):
                    if i == len(value)-1 and len(value) >= 2: r += " kaj"
                    elif i > 0: r += ","
                    r += " " + lingvonomo(db[f'ling_nom_{value[i]}'])
        else:
            r += "Nenio ŝanĝiĝis\n"
            if len(value) == 0: r += f"Vi ne havas denaskulajn rolojn"
            else:
                r += f"Vi havas la rolo{'j' if len(value) > 1 else ''}n kiel denaskulo de"
                for i in range(0, len(value)):
                    if i == len(value)-1 and len(value) >= 2: r += " kaj"
                    elif i > 0: r += ","
                    r += " " + lingvonomo(db[f'ling_nom_{value[i]}'])
        await ctx.send(r, ephemeral=False)  
        
    
    @lingvo.subcommand()
    @interactions.option(
        description="Kodo de la lingvo laŭ ISO 639-3",
        autocomplete=True,
        required=True,
    )
    @interactions.option(
        description="Rolo destinita por denaskuloj de la lingvo. Lasu malplena por nuligi",
        required=False,
    )
    @interactions.option(
        description="Rolo destinita por lernantoj de la lingvo. Lasu malplena por nuligi",
        required=False,
    )
    async def roloj(self, ctx, kodo: str, rolo_denaske: interactions.Role = None, rolo_lernate: interactions.Role = None):
        """Ligi kaj malligi rolojn al lingvo"""
        eligo = f"{lingvonomo(db[f'ling_nom_{kodo}'], ekmajuskle = True)}:\n"
        enas_d = f"ling_rol_den_{int(ctx.guild.id)}_{kodo}" in db.keys()
        enas_l = f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}" in db.keys()
        f = not ((rolo_denaske == None and enas_d) or (not enas_d or db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"] != str(rolo_denaske.id))) and not ((rolo_lernate == None and enas_l) or (not enas_l or db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"] != str(rolo_denaske.id)))
        await ctx.defer()
        if rolo_denaske == None and enas_d:
            f = True
            del db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"]
            eligo += "La denaskula rolo malligiĝis\n"
        elif not enas_d or db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"] != str(rolo_denaske.id):
            f = True
            if str(rolo_denaske.id) in db.values():
                lingvokodo = sxlosilo_el_valoro(str(rolo_denaske.id), "ling_rol_").split('_').last()
                rolnomo1 = (await interactions.get(self.client, interactions.Role,
                    parent_id=int(ctx.guild.id),
                    object_id=db[f"ling_rol_den_{int(ctx.guild.id)}_{lingvokodo}"]
                )).mention
                rolnomo2 = (await interactions.get(self.client, interactions.Role, 
                    parent_id=int(ctx.guild.id),
                    object_id=db[f"ling_rol_lern_{int(ctx.guild.id)}_{lingvokodo}"]
                )).mention 
                eligo += f"""La rolo {rolo_denaske.mention} jam uziĝas por iu lingvo:
                > `{lingvokodo}` ({lingvonomo(db[f'ling_nom_{lingvokodo}'])}), roloj: {rolnomo1}, {rolnomo2}
                """
            else:
                db[f"ling_rol_den_{int(ctx.guild.id)}_{kodo}"] = str(rolo_denaske.id)
                eligo += f"La rolo {rolo_denaske.mention} ligiĝis kiel denaskula\n"
        if rolo_lernate == None and enas_l:
            f = True
            del db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"]
            eligo += "La lernantula rolo malligiĝis"
        elif not enas_l or db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"] != str(rolo_lernate.id):
            f = True
            if str(rolo_lernate.id) in db.values():
                lingvokodo = sxlosilo_el_valoro(str(rolo_lernate.id), "ling_rol_").split('_').last()
                rolnomo1 = (await interactions.get(self.client, interactions.Role,
                    parent_id=int(ctx.guild.id),
                    object_id=db[f"ling_rol_den_{int(ctx.guild.id)}_{lingvokodo}"]
                )).mention
                rolnomo2 = (await interactions.get(self.client, interactions.Role, 
                    parent_id=int(ctx.guild.id),
                    object_id=db[f"ling_rol_lern_{int(ctx.guild.id)}_{lingvokodo}"]
                )).mention 
                eligo += f"""La rolo {rolo_lernate.mention} jam uziĝas por iu lingvo:
                > `{lingvokodo}` ({lingvonomo(db[f'ling_nom_{lingvokodo}'], plena = False)}), roloj: {rolnomo1}, {rolnomo2}"""
            else:
                db[f"ling_rol_lern_{int(ctx.guild.id)}_{kodo}"] = str(rolo_lernate.id)
                eligo += f"La rolo {rolo_lernate.mention} ligiĝis kiel lernantula"
        if not f: await ctx.send("Nenio ŝanĝiĝis", ephemeral=True)
        else: await ctx.send(eligo)
    
    @interactions.extension_autocomplete("lingvo", "kodo")
    async def kodo_autocomplete(self, ctx, value = ""):
        keys_nom = db.prefix(f"ling_nom_")
        id = len(f"ling_nom_")
        elektoj = [interactions.Choice(name=f"{sxlosilo[id:]} ({lingvonomo(db[sxlosilo], ekmajuskle = True)})", value=sxlosilo[id:]) for sxlosilo in keys_nom if value in sxlosilo[id:]]
        await ctx.populate(elektoj)

def setup(client):
    Lingvo(client)