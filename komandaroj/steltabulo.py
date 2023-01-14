import interactions
import os
from replit import db
from komandaroj.cxiaj import reaguma_kvanto, kunigi
from PIL import Image
from urllib.request import urlopen

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
USERNAME = str(os.environ['USERNAME_DISCRIMINATOR'])


class Steltabulo(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.agordmesagxo: interactions.Message = None

    # KOMANDO /STELTABULO
    @interactions.extension_command(
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=GUILD)
    async def steltabulo(self, ctx):
        return None

    # /STELTABULO AGORDI
    @steltabulo.subcommand()
    @interactions.option(
        description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn")
    @interactions.option(
        description=
        "Kiom da steloj estu por ke la afiŝo ensteltabuliĝu. Defaŭlte: 4")
    async def agordi(self, ctx, kanalo: interactions.Channel, kvanto: int = 4):
        """Agordi la steltabulon (uzeblas ankaŭ por la unua aktivigo)"""
        self.agordmesagxo = await ctx.send(
            f"**Agordado...**\n" \
            f"> _Kanalo:_ <#{kanalo.id}>\n" \
            f"> _Minimume da steloj:_ {kvanto}\n" \
            f"> _La emoĝio:_ `neniu, bonvolu reagumi per la taŭga emoĝio`"
        )
        db[f"steltabulo_{ctx.guild.id}_kanalo"] = str(kanalo.id)
        db[f"steltabulo_{ctx.guild.id}_kvanto"] = str(kvanto)
        del db[f"steltabulo_{ctx.guild_id}_emogxio"]

    # PRITRAKTADO DE ALDONOJ DE REAGUMOJ
    @interactions.extension_listener()
    async def on_message_reaction_add(self,
                                      reagumo: interactions.MessageReaction):
        if (f"steltabulo_{reagumo.guild_id}_kanalo"
                in db.prefix("steltabulo_")):

            if ((self.agordmesagxo != None) and (reagumo.message_id == self.agordmesagxo.id)):
                kanalo = await self.agordmesagxo.get_channel()
                await self.agordmesagxo.edit(
                    f"**Sukcese agordite**\n" \
                    f"> _Kanalo:_ <#{kanalo.id}>\n" \
                    f"> _Minimume da steloj:_ {db[f'steltabulo_{reagumo.guild_id}_kvanto']}\n" \
                    f"> _La emoĝio:_ {reagumo.emoji} (ID: `{reagumo.emoji.id if (reagumo.emoji.id != None) else 'Nula'}`, nomo: `{reagumo.emoji.name}`)"
                )
                self.agordmesagxo = None
                db[f"steltabulo_{str(reagumo.guild_id)}_emogxio"] = \
                f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"

            elif (f"steltabulo_{reagumo.guild_id}_emogxio"
                  in db.prefix("steltabulo_")):
                e_id = db[f"steltabulo_{reagumo.guild_id}_emogxio"]
                if (e_id[0] == 'i'):
                    emogxio = await interactions.get(
                        self.client,
                        interactions.Emoji,
                        object_id=e_id[1:],
                        parent_id=reagumo.guild_id)
                else:
                    emogxio = interactions.Emoji(name=e_id[1:])

                if (str(reagumo.emoji) == str(emogxio)):
                    mesagxo = await interactions.get(
                        self.client,
                        interactions.Message,
                        object_id=reagumo.message_id,
                        parent_id=reagumo.channel_id,
                        force="http")
                    kvanto = reaguma_kvanto(mesagxo, emogxio)
                    reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
                    uzantnomoj = [f"{u.username}#{u.discriminator}" for u in reagumintoj]

                    if (kvanto >= int(
                            db[f"steltabulo_{reagumo.guild_id}_kvanto"])
                            and USERNAME not in uzantnomoj):
                        await mesagxo.create_reaction(emogxio)

                        kanalo = await interactions.get(
                            self.client,
                            interactions.Channel,
                            object_id=db[f"steltabulo_{reagumo.guild_id}_kanalo"])
                        mesagxkanalo = await mesagxo.get_channel()
                        gildaid = reagumo.guild_id
                        ano = await interactions.get(
                            self.client,
                            interactions.Member,
                            object_id=mesagxo.author.id,
                            parent_id=gildaid)
                        avataro = ano.get_avatar_url(gildaid)
                        if (avataro == None):
                            avataro = mesagxo.author.avatar_url
                        nomo = ano.nick
                        if (nomo == None):
                            nomo = mesagxo.author.username
                        aldonajxoj = "> _Tipoj de la aldonajxoj:_"
                        bildoj = []
                        bilda_ligilo = None
                        for a in mesagxo.attachments:
                            aldonajxoj = aldonajxoj + f"\n> {a.content_type} ({a.content_type[:5]})"
                            if (a.content_type[:6] == "image/" and bilda_ligilo == None):
                                bilda_ligilo = a.url
                            #    bildoj.append(Image.open(urlopen(a.url)))
                        
                        if (len(bildoj) != 0):
                            bildo = kunigi(bildoj)
                            bd_nomo = f"bildo_{kanalo.id}_{mesagxo.id}.jpg"
                            bildo.save(bd_nomo)

                        plusenhavo = interactions.Embed(
                            author=interactions.EmbedAuthor(
                                name=nomo,
                                icon_url=avataro,
                            ),
                            description=mesagxo.content,
                            timestamp=mesagxo.timestamp,
                            color=0x1EC34B,
                            image=interactions.EmbedImageStruct(url=bilda_ligilo) if (bilda_ligilo != None) else None,
                        )

                        await kanalo.send(
                            content=f"<#{mesagxkanalo.id}> {mesagxo.url}\n" \
                            f"{emogxio} x{kvanto}\n" \
                            f"`Tipo de la mesaĝo: {mesagxo.type}`\n" \
                            + aldonajxoj,
                            embeds=plusenhavo
                        )


def setup(client):
    Steltabulo(client)
