import interactions
import os
from replit import db
import re
import cxiaj as c

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
CHANNEL = int(os.environ['ESPERANTO_CHANNEL_ID'])
ID = int(os.environ['BOT_ID'])

class Testo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.lasta_forigmesagxo = None
        self.forigprefikso = None

    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD)
    async def testo(self, ctx):
        return None

    @testo.subcommand()
    @interactions.option(
        str,
        name="opcio",
        description="Testa opcio",
        #autocomplete=True,
    )
    async def testa(self, ctx, opcio: interactions.Channel):
        """Testa komando"""
        await ctx.send(
            f"<#{opcio.id}>\n" \
        )
        robota_ano = await interactions.get(
            self.client,
            interactions.Member,
            object_id = ID,
            parent_id = GUILD,
        )
        #permesoj = await robota_ano.has_permissions(interactions.Permissions.VIEW_CHANNEL, interactions.Permissions.SEND_MESSAGES, )
        #print(permesoj)

    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD,
    )
    async def datumbazo(self, ctx):  #database
        return None

    @datumbazo.subcommand()
    async def listigi(self, ctx):
        """Montri la enhavon de la datumbazo"""  
        s = "Jen la enhavo de la datumbazo:\n"  
        for sxlosilo in db.keys():
            if (len(db[sxlosilo])<100):
                s += f"`{sxlosilo}`: {f'`{db[sxlosilo]}`' if (db[sxlosilo] != '') else 'Nula signovico'}\n"  #"[key]: [value]"
            else:
                s += f"`{sxlosilo}`: `{db[sxlosilo][:100]}`...\n"
        await ctx.send(s)

    @datumbazo.subcommand()
    @interactions.option(
        description="La anstataŭigenda signovico",  #the string to be replaced
        required=True,
    )
    @interactions.option(
        description="La anstataŭonta signovico",  #the string to replace with
        required=True,
    )
    async def anstatauxigi(self, ctx, kion: str, per_kio: str):  #replace in keys
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
        plp = "j" if p != 1 else ""
        await ctx.send(
            f"Farite\n" \
            f"Ŝlosilo{plk} de {k} elemento{plk} estis renomita{plk}\n"  \
            f"{f'{p} ŝlosilo{plp} ne renomeblis pro ekzisto de aliaj samnomaj ŝlosiloj' if p > 0 else ''}"
        )

    @datumbazo.subcommand()
    @interactions.option(
        description="La prefikso de la forigendaj ŝlosiloj",
        required=True,
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
            b = interactions.Button(style=interactions.ButtonStyle.DANGER,
                                    label="Jes, forigi",
                                    custom_id="forigi_el_datumbazo")
            plk = "j" if k > 1 else ""
            s = f"Vi volas forigi el la datumbazo {k} elemento{plk}n:\n{s}" if (len(s) < 1800) else f"Vi volas forigi el la datumbazo {k} elemento{plk}n"
            self.forigprefikso = kion
            if self.lasta_forigmesagxo != None:
                await self.lasta_forigmesagxo.disable_all_components()
            self.lasta_forigmesagxo = await ctx.send(s, components=b)

    @interactions.extension_component("forigi_el_datumbazo")
    async def forigi_el_datumbazo(self, ctx):
        for sxlosilo in db.prefix(self.forigprefikso):
            del db[sxlosilo]
        await self.lasta_forigmesagxo.disable_all_components()
        await ctx.send("La elementoj foriĝis")

    @interactions.extension_autocomplete("testo", "opcio")
    async def testo_autocomplete(self, ctx, value=""):
        koloroj = ["bluo", "verdo", "flavo", "ruĝo", "blanko", "nigro"]
        elektoj = [
            interactions.Choice(name=koloro, value=koloro)
            for koloro in koloroj if value in koloro
        ]
        await ctx.populate(elektoj)

    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD,
    )
    @interactions.option(
        description="Kion diri",
    )
    async def diri(self, ctx, dirajxo: str):
        """Diri ion en la nomo de la roboto"""
        await ctx.send(f"Laŭ cia peto, mi sendis la sekvan mesaĝon:\n\n{dirajxo}", ephemeral=True)
        kanalo = await interactions.get(
            self.client,
            interactions.Channel,
            object_id=ctx.channel_id,
            parent_id=ctx.guild_id,
        )
        await kanalo.send(dirajxo)

    @interactions.extension_command(
        type=interactions.ApplicationCommandType.MESSAGE,
        name="Resendi la mesaĝon",
        scope=GUILD,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    )
    async def la_mesagxa_objekto(self, ctx):
        kanalo = await interactions.get(
            self.client,
            interactions.Channel,
            object_id=CHANNEL,
            parent_id=GUILD,
        )
        #mesagxo = re.sub(r"([\(,\[])", r"\1\n", str(ctx.target))
        print(str(ctx.target))
        respondo = f"Sendite al <#{CHANNEL}>."
        if (len(str(ctx.target)) > 1900):
            respondo += "\n⚠️ La mesaĝa objekto estas tro longa. Vidu ĝin en la konzolo."
        else:
            await kanalo.send(f'La mesaĝa objekto:\n```py\n{str(ctx.target)}```')
        await kanalo.send(f'La plusenhavo:', embeds=c.plusenhavo_el_mesagxo(self, ctx.target, GUILD))
        await ctx.send(respondo, ephemeral=True)

def setup(client):
    Testo(client)
