import hikari
import lightbulb
import re
import datetime as dt
from configparser import ConfigParser
from ansi import ansi_code, Format, TextColor
from utils import get_author_member, emoji_from_string, string_from_emoji, \
    author_reacted, strif, require_confirmation, UserIsWrong, owner_only
from utils_db import Database
from utils_eo import get_color, human_readable_time, plural, kaj_join, BOOLEAN_CHOICES

# tipoj de aŭdvidaĵoj {angle: esperante}
MEDIA_TYPES = {
    "application": "dosiero",
    "audio": "aŭdaĵo",
    "channel": "kanalo",
    "embed": "informujo",
    "image": "bildo",
    "message": "mesaĝo",
    "model": "3D-modelo",
    "music": "muzikaĵo",
    "post": "afiŝo",
    "text": "tekstaĵo",
    "video": "filmo",
}
EMBED_PROVIDERS = {
    "YouTube": "video",
    "Spotify": "music",
    "Apple Music": "music"
}
SPECIAL_MESSAGES = {
    hikari.MessageType.CHANNEL_PINNED_MESSAGE: "{uzanto} fiksis mesaĝon en la kanalo",
    hikari.MessageType.GUILD_MEMBER_JOIN: "{uzanto} aliĝis al la servilo",
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION: "{uzanto} ĵus nitrumis la servilon[[ {enhavo} fojojn]]",
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1: "{uzanto} ĵus nitrumis la servilon[[ {enhavo} fojojn]] ĝis la unua nivelo",
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: "{uzanto} ĵus nitrumis la servilon[[ {enhavo} fojojn]] ĝis la dua nivelo",
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: "{uzanto} ĵus nitrumis la servilon[[ {enhavo} fojojn]] ĝis la tria nivelo",
}

GREEN = get_color("Verdo")
TEAL = get_color("Turkiskoloro")

MAX_DELTA = dt.timedelta(days=30).total_seconds()

EMBED_DESC_LIMIT = 4000
REQ_POINTS_DEFAULT = 1
# La unua spaceto estas N-spaceto
FOOTER_SEPARATOR = " • "

DATABASE = Database("Steltabulo")

config = ConfigParser()
config.read("config.ini")
data = config["datumoj"]
ME = int(data["roboto"])

loader = lightbulb.Loader()

class StarboardSettings():
    def __init__(self, guild_id: int, **parameters):
        """
        Agordi aŭ ŝargi la agordojn de steltabulo

        `guild_id`
            La identigilo de la servilo
        `**parameters`
            La agordoj. Ellasu por ŝargi
            la agordojn el la datumbazo
        
        La parametroj
        -------------
        `channel` (hikari.GuildChannel)
            La steltabula kanalo
        `upvote_emoji` (str)
            La pora reago
        `downvote_emoji` (str)
            La kontraŭa reago
        `required_points` (int)
            Kiom da poentoj akirendas por ensteltabuliĝo
        `self_votes` (bool)
            Voĉdonoj pri siaj mesaĝoj
        `star_blocking` (bool)
            Blokeblo
        """
        self.__guild_id = guild_id

        self.__channel_id: int = None
        self.__channel: hikari.GuildChannel = None
        self.__upvote_emoji_str: str = None
        self.__upvote_emoji: hikari.Emoji = None
        self.__downvote_emoji_str: str = None
        self.__downvote_emoji: hikari.Emoji = None
        self.__required_points: int = REQ_POINTS_DEFAULT
        self.__self_votes = False
        self.__star_blocking = False

        if not parameters:
            if str(guild_id) not in DATABASE: 
                raise UserIsWrong(
                    "En via servilo ne estas aktiva steltabulo. "
                    "Agordu steltabulon per «/steltabulon aktivigi»"
                )
            parameters = DATABASE[str(guild_id)]["Settings"]
        
        self.update_parameters(**parameters, assert_req=True)
    
    def __repr__(self) -> str:
        return (f"<Steltabula agordaro: "
                f"kanala ID = {self.__channel_id}, "
                f"pora reago = {self.__upvote_emoji_str}, "
                f"kontraŭa reago = {self.__downvote_emoji_str}, "
                f"voĉdonoj por si = {self.__self_votes}, "
                f"blokeblo = {self.__star_blocking}>")

    def display_settings(self) -> str:
        display = f"La kanalo: <#{self.__channel_id}>\n"
        display += f"La emoĝio por pora voĉdono: {self.__upvote_emoji_str}\n"
        if self.__downvote_emoji_str:
            display += f"La emoĝio por kontraŭa voĉdono: {self.__downvote_emoji_str}\n"
        display += f"Por ensteltabuliĝo necesas **almenaŭ {self.__required_points} poento{plural(self.__required_points)}**\n"
        display += f"Voĉdonoj de la aŭtoroj **{strif(not self.__self_votes, 'ne ')}enkalkuliĝas**\n"
        if self.__downvote_emoji_str:
            display += f"La aŭtoroj **{strif(not self.__star_blocking, 'ne ')}povas malpermesi** ensteltabuliĝon\n"
        return display

    def __update_in_database(self, key: str, value):
        if str(self.__guild_id) not in DATABASE:
            DATABASE[str(self.__guild_id)] = {"Settings": {}, "Posted": {}}
        DATABASE[str(self.__guild_id)]["Settings"][key] = value

    def __database_key_value(self, key: str, value, update: bool) -> dict[str]:
        if update:
            self.__update_in_database(key, value)
        return {key: value}

    def channel_is(self, channel: hikari.PartialChannel | int) -> bool:
        if isinstance(channel, hikari.PartialChannel):
            channel = channel.id
        return channel == self.__channel_id

    @property
    def channel_id(self) -> int:
        return self.__channel_id

    @lightbulb.di.with_di
    async def get_channel(self, rest: hikari.api.RESTClient = lightbulb.di.INJECTED) -> hikari.GuildChannel:
        if not self.__channel:
            self.__channel = await rest.fetch_channel(self.__channel_id)
        return self.__channel
    
    def set_channel(self, value: hikari.PartialChannel | int, update: bool = True) -> dict[str]:
        if isinstance(value, hikari.PartialChannel):
            self.__channel = value
            self.__channel_id = value.id
        else:
            self.__channel_id = value
            self.__channel = None
        return self.__database_key_value("channel", self.__channel_id, update)
    
    @property
    def upvote_emoji_mention(self) -> str:
        return self.__upvote_emoji_str

    @lightbulb.di.with_di
    async def get_upvote_emoji(self, rest: hikari.api.RESTClient = lightbulb.di.INJECTED) -> hikari.Emoji:
        """La emoĝio por voĉdoni por mesaĝoj"""
        if not self.__upvote_emoji:
            self.__upvote_emoji = await emoji_from_string(self.__upvote_emoji_str, self.__guild_id, rest)
        return self.__upvote_emoji
    
    def set_upvote_emoji(self, value: hikari.Emoji | str, update: bool = True) -> dict[str]:
        emoji_string = string_from_emoji(value)
        self.__upvote_emoji_str = emoji_string
        if isinstance(value, hikari.Emoji):
            self.__upvote_emoji = value
        else:
            self.__upvote_emoji = None
        return self.__database_key_value("upvote_emoji", self.__upvote_emoji_str, update)
    
    @property
    def downvote_emoji_mention(self) -> str | None:
        return self.__downvote_emoji_str

    @lightbulb.di.with_di
    async def get_downvote_emoji(self, rest: hikari.api.RESTClient = lightbulb.di.INJECTED) -> hikari.Emoji | None:
        """La emoĝio por voĉdoni kontraŭ mesaĝoj"""
        if not self.__downvote_emoji_str:
            return None
        if not self.__downvote_emoji:
            self.__downvote_emoji = await emoji_from_string(self.__downvote_emoji_str, self.__guild_id, rest)
        return self.__downvote_emoji
    
    def set_downvote_emoji(self, value: hikari.Emoji | str | None, update: bool = True) -> dict[str]:
        if not value:
            self.__downvote_emoji = None
            self.__downvote_emoji_str = None
        emoji_string = string_from_emoji(value)
        self.__downvote_emoji_str = emoji_string
        if isinstance(value, hikari.Emoji):
            self.__downvote_emoji = value
        else:
            self.__downvote_emoji = None
        return self.__database_key_value("downvote_emoji", self.__downvote_emoji_str, update)

    @property
    def required_points(self) -> int:
        """Kiom da poentoj akirendas por ensteltabuliĝo"""
        return self.__required_points
    
    def set_required_points(self, value: int, update: bool = True) -> dict[str]:
        if value <= 0:
            raise UserIsWrong(f"La kvanto de havendaj poentoj estu pozitiva")
        self.__required_points = value
        return self.__database_key_value("required_points", self.__required_points, update)

    @property
    def self_votes(self) -> bool:
        """Ĉu enkalkulendu la voĉdonoj de la aŭtoro de la mesaĝo"""
        return self.__self_votes
    
    def set_self_votes(self, value: int | bool, update: bool = True) -> dict[str]:
        if isinstance(value, int):
            value = (value > 0)
        self.__self_votes = value
        return self.__database_key_value("self_votes", self.__self_votes, update)

    @property
    def star_blocking(self) -> bool:
        return self.__star_blocking
    
    def set_star_blocking(self, value: int | bool, update: bool = True) -> dict[str]:
        if isinstance(value, int):
            value = (value > 0)
        self.__star_blocking = value
        return self.__database_key_value("star_blocking", self.__star_blocking, update)

    __SETTERS = {
        "channel": set_channel,
        "upvote_emoji": set_upvote_emoji,
        "downvote_emoji": set_downvote_emoji,
        "required_points": set_required_points,
        "self_votes": set_self_votes,
        "star_blocking": set_star_blocking
    }

    __REQUIRED = ["channel", "upvote_emoji"]
    __REQUIRE_DB_CLEARUP = ["channel", "upvote_emoji", "downvote_emoji"]

    def update_parameters(self, **parameters):
        """
        Ŝanĝi la agordojn de la steltabulo

        `assert_req`
            Ĉu kontroli difinitecon de ĉiuj steltabulaj parametroj
        `clear_if_edited`
            Ĉu forigi la steltabulajn afiŝojn el la datumbazo, se
            grava parametro ŝanĝiĝis
        
        Eblaj parametroj
        ----------------
        `channel` (hikari.GuildChannel)
            La steltabula kanalo
        `upvote_emoji` (str)
            La pora reago
        `downvote_emoji` (str)
            La kontraŭa reago
        `required_points` (int)
            Kiom da poentoj akirendas por ensteltabuliĝo
        `self_votes` (bool)
            Voĉdonoj pri siaj mesaĝoj
        `star_blocking` (bool)
            Blokeblo    
        """
        assert_req = parameters.pop("assert_req", False)
        clear_if_edited = parameters.pop("clear_if_edited", False)
        if assert_req:
            for name in StarboardSettings.__REQUIRED:
                if name not in parameters:
                    raise ValueError(f"En la steltabula mankas valoro {name}")
        if clear_if_edited:
            for name in StarboardSettings.__REQUIRE_DB_CLEARUP:
                if name in parameters:
                    DATABASE[str(self.__guild_id)]["Posted"] = {}
                    break
        new_parameters = {}
        for name, setter in StarboardSettings.__SETTERS.items():
            if name in parameters:
                new_parameters |= setter(self, parameters.pop(name), update=False)
        # Endatumbazigi la ŝanĝojn nur post sukcesa plenumiĝo de ĉiuj reagordoj
        for k, v in new_parameters.items():
            self.__update_in_database(k, v)


def media_type_from_embed(embed: hikari.Embed) -> str | None:
    """
    Tipo de aŭdvidaĵo prezentita per informujo

    `embed`
        la informujo
    """
    if not embed.provider:
        if embed.video:
            return "video"
        if embed.footer and (embed.footer.text.lower() == "twitter"):
            return "post"
        return "embed"
    return EMBED_PROVIDERS.get(embed.provider.name, "embed")

def media_description(media_type_title: str, file_name: str):
    return (
        f"```ansi\n"
        f"{media_type_title}\n"
        f"{ansi_code(TextColor.BLUE, format=Format.BOLD)}{file_name}{ansi_code()}"
        f"```"""
    )

def incorporate_embed(embed: hikari.Embed, occupied_len: int) -> tuple[hikari.Attachment | None, str | None]:
    """
    La enhavo de informujo en formo, prezentebla interne de alia informujo

    `embed`
        la internigenda informujo
    `occupied_len`
        kiom da simboloj jam estas en la ekstera informujo
    """
    attachment = None
    description = None
    if not embed.provider:
        if embed.description and "```" in embed.description:
            return None, None
        if embed.total_length() + occupied_len > EMBED_DESC_LIMIT:
            return None, None
        attachment = embed.image or embed.thumbnail
        match embed.url:
            case None: title_style = {"text_color": TextColor.WHITE, "format": Format.BOLD}
            case _: title_style = {"text_color": TextColor.BLUE, "format": Format.BOLD | Format.UNDERLINE}
        description = (
            (f"{ansi_code(**title_style)}{embed.title}{ansi_code()}\n" if embed.title else "")
            + (f"{ansi_code(TextColor.WHITE)}{embed.author.name}{ansi_code()}\n" if embed.author else "")
            + (f"{embed.description}\n" if embed.description else "\n")
        )
        if embed.fields:
            for field in embed.fields:
                description += (
                    ansi_code(TextColor.WHITE, format=Format.BOLD)
                    + field.name + "\n"
                    + ansi_code(format=Format.NONE)
                    + field.value
                    + ansi_code() + "\n"
                )
        if embed.footer or embed.timestamp:
            description += (
                ansi_code(TextColor.GRAY)
                + (embed.footer.text if embed.footer else "")
                + (FOOTER_SEPARATOR if embed.footer and embed.timestamp else "")
                + (human_readable_time(embed.timestamp) if embed.timestamp else "")
                + ansi_code()
            )
        return attachment, f"```ansi\n{description}```"
    if media_type := media_type_from_embed(embed):
        attachment = embed.thumbnail
        description = (
            f"{MEDIA_TYPES[media_type].capitalize()} el {embed.provider.name}\n"
            f"\n"
            + (f"{ansi_code(TextColor.WHITE, format=Format.BOLD)}{embed.author.name}{ansi_code()}\n" if embed.author else "")
            + (f"{ansi_code(TextColor.BLUE, format=Format.BOLD|Format.UNDERLINE)}{embed.title}{ansi_code()}\n" if embed.title else "")
            + (f"{embed.description}\n" if embed.description else "")
        )
    return attachment, f"```ansi\n{description}```"

def parse_attachments(
    attachments: list[hikari.Attachment],
    embeds: list[hikari.Embed],
    occupied_len: int
) -> tuple[hikari.Attachment | None, str | None, dict[str, int]]:
    """
    Analizi la kunsendaĵojn

    `attachments`
        la kunsendaĵoj
    `embeds`
        la informujoj
    `occupied_len`
        Kiom da simboloj jam estas en la ekstera informujo

    La rezulto konsistas el:

    `main_attachment`
        la unua kunsendaĵo, t.e. la demonstrenda
    `main_description`
        la priskribo ĉe la demonstrenda kunsendaĵo
    `numbers_of_attachments`
        la kvantoj de ĉiuj ceteraj kunsendaĵoj laŭtipe
    """
    main_attachment = None
    main_description = None
    numbers_of_attachments = dict()
    for attachment in attachments:
        media_type: re.Match = re.match(r"[^/]+(?=/)", attachment.media_type)
        if not media_type:
            raise ValueError(f"La kunsendaĵo {attachment} havas neatenditan tipon: {attachment.media_type}")
        media_type = media_type.group()
        if main_attachment:
            numbers_of_attachments[media_type] = numbers_of_attachments.get(media_type, 0) + 1
            continue
        else:
            main_attachment = attachment
            match media_type:
                case "video" | "application":
                    if attachment.title:
                        ext = attachment.filename[attachment.filename.rfind(".") :]
                        filename = attachment.title + ext
                    else:
                        filename = attachment.filename
                    main_description = media_description(
                        f"Kunsendita {MEDIA_TYPES[media_type]}", filename
                    )
    for embed in embeds:
        if not (main_attachment or main_description):
            main_attachment, main_description = incorporate_embed(embed, occupied_len)
            if main_attachment or main_description:
                continue
        media_type = media_type_from_embed(embed)
        if media_type == "embed" and embed.provider:
            print(f"! La informujo {embed} havas nekonatan fonton: {embed.provider} ({embed.url})")
        numbers_of_attachments[media_type] = numbers_of_attachments.get(media_type, 0) + 1
    return main_attachment, main_description, numbers_of_attachments


async def embedify(
        message: hikari.Message, 
        guild_id: int,
        title: str = None, 
        url: str = None,
        link_the_message: bool = False,
        color: hikari.Colorish = TEAL
    ) -> hikari.Embed:
    """
    Informujigi

    `title`
        la titolo de la informujo
    `url`
        la ligilo ĉe la informujo
    `link_the_message`
        ĉu ligi al la mesaĝo (preferata ol `url`)
    `color`
        la koloro de la maldekstra linio de la informujo
    """
    is_special = message.type in SPECIAL_MESSAGES
    embed = hikari.Embed(
        title=title,
        description=(
            message.content if not is_special else 
            message.message_reference.message_link if message.message_reference else None
        ),
        url=message.make_link(message.guild_id) if link_the_message else url,
        color=color,
        timestamp=message.timestamp,
    )
    footer_info = []

    # La aŭtoro
    author = await get_author_member(message, guild_id)
    name = author.display_name
    if author.is_bot: name = "[🤖] " + name
    if is_special:
        string = SPECIAL_MESSAGES[message.type]
        if "[[" in string and not message.content:
            string = re.sub(r"\[\[.+?\]\]", "", string)
        name = string.format(uzanto=name, enhavo=message.content) # , mesaĝo=message.message_reference.message_link
    embed.set_author(name=name, icon=author.display_avatar_url)
    if is_special:
        return embed

    # la kunsendaĵoj (inkl. el ceteraj sociretoj)
    main_attachment, attachment_description, numbers_of_attachments = parse_attachments(
        message.attachments,
        message.embeds,
        len(embed.description) if embed.description else 0,
    )
    if main_attachment:
        embed.set_image(main_attachment.url)
    if attachment_description:
        if not embed.description: embed.description = ""
        embed.description += "\n" + attachment_description
    if numbers_of_attachments:
        footer_info.append("❗+ " + kaj_join([f"{n} {MEDIA_TYPES[mt]}{plural(n)}" for mt, n in numbers_of_attachments.items()]))

    # Respondaj mesaĝoj
    if message.type == hikari.MessageType.REPLY:
        # La mesaĝo reakirendas, sen tio la respondata mesaĝo ne estos akirebla
        # (Diskordo ne sendas la datumon)
        message = await message.app.rest.fetch_message(message.channel_id, message.id)
        if message.referenced_message:
            replied_message: hikari.Message = message.referenced_message
            replied_author = await get_author_member(replied_message, guild_id)
            footer_info.append(f"↩️ Responde al {replied_author.display_name}")

    # Enmeti ĉiujn subinformojn
    embed.set_footer(FOOTER_SEPARATOR.join(footer_info) if footer_info else None)

    return embed

@lightbulb.di.with_di
async def message_points(
    event: hikari.GuildReactionAddEvent 
    | hikari.GuildReactionDeleteEmojiEvent 
    | hikari.GuildReactionDeleteEvent 
    | hikari.GuildReactionDeleteAllEvent, 
    message: hikari.Message,
    settings: StarboardSettings,
    rest: hikari.api.RESTClient = lightbulb.di.INJECTED
) -> tuple[tuple[int, int] | None, bool]:
    """
    Kiom da poraj kaj kontraŭaj voĉdonoj
    havas la mesaĝo, kies reagaro ŝanĝiĝis.

    Se la ŝanĝo ne estas grava, rezultas `None`. 

    La dua valoro montras, ĉu la mesaĝo eble ensteltabuliĝu
    """
    if isinstance(event, hikari.GuildReactionDeleteAllEvent):
        return (0, 0), False
    upvote_emoji = await settings.get_upvote_emoji()
    downvote_emoji = await settings.get_downvote_emoji()
    if not (event.is_for_emoji(upvote_emoji) or (downvote_emoji and event.is_for_emoji(downvote_emoji))):
        return None, False
    upvotes = 0
    downvotes = 0
    candidate = True
    for reaction in message.reactions:
        if reaction.emoji.mention == upvote_emoji.mention:
            upvotes += reaction.count
            if reaction.is_me:
                candidate = False
                upvotes -= 1
        elif reaction.emoji.mention == downvote_emoji.mention:
            downvotes += reaction.count
    self_votes = settings.self_votes
    star_blocking = settings.star_blocking
    if self_votes and not star_blocking:
        return (upvotes, downvotes), candidate
    author_upvoted = False
    author_downvoted = False
    author_downvoted = await author_reacted(message, downvote_emoji)
    if star_blocking and author_downvoted:
        candidate = False
    if self_votes:
        return (upvotes, downvotes), candidate
    author_upvoted = await author_reacted(message, upvote_emoji)
    if author_upvoted:
        upvotes -= 1
    if author_downvoted:
        downvotes -= 1
    return (upvotes, downvotes), candidate

def clear_up_starboard_posts(guild_id: int):
    now = dt.datetime.now().timestamp()
    posts = dict(DATABASE[str(guild_id)]["Posted"])
    for msg, post_data in posts.items():
        if now - post_data["Timestamp"] >= MAX_DELTA:
            del DATABASE[str(guild_id)]["Posted"][msg]

@loader.command
class Informujigi(
    lightbulb.MessageCommand,
    name = "Informujigi",
    hooks = [owner_only],
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context):
        message = self.target
        embed = await embedify(message, guild_id=ctx.guild_id)
        response = await ctx.fetch_response(
            await ctx.respond(embed, ephemeral=True)
        )

@loader.command
class Sencimigo(
    lightbulb.MessageCommand,
    name = "Sencimigo",
    hooks = [owner_only],
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context):
        message = self.target
        print(message)
        print(message.type)
        print(message.content)
        print()
        print(message.message_reference)
        print()
        print(message.attachments)
        if message.attachments:
            attachment = message.attachments[0]
            print(
                attachment.duration, attachment.filename, attachment.height, attachment.id,
                attachment.is_ephemeral, attachment.media_type, attachment.proxy_url, attachment.size,
                attachment.url, attachment.waveform, attachment.width,
                sep="\n"
            )
        print()
        print(message.embeds)
        if message.embeds:
            embed = message.embeds[0]
            print(
                embed.author, embed.description, embed.fields, embed.footer, embed.image, embed.provider,
                embed.thumbnail, embed.timestamp, embed.title, embed.url, embed.video,
                sep="\n"
            )
        await ctx.respond("Rigardu la informojn en la konzolo", ephemeral=True)

@loader.listener(hikari.GuildReactionEvent)
@lightbulb.di.with_di
async def reaction(
    event: hikari.GuildReactionAddEvent 
    | hikari.GuildReactionDeleteEmojiEvent 
    | hikari.GuildReactionDeleteEvent 
    | hikari.GuildReactionDeleteAllEvent, 
    rest: hikari.api.RESTClient = lightbulb.di.INJECTED
):
    if isinstance(event, (hikari.GuildReactionAddEvent, hikari.GuildReactionDeleteEvent)) and event.user_id == ME:
        return
    guild_id = event.guild_id
    if str(guild_id) not in DATABASE:
        return
    settings = StarboardSettings(guild_id)
    if event.channel_id == settings.channel_id:
        return
    message = await rest.fetch_message(event.channel_id, event.message_id)
    now = dt.datetime.now().timestamp()
    if now - message.timestamp.timestamp() >= MAX_DELTA:
        return
    points, candidate = await message_points(event, message, settings)
    if not points:
        return
    upvotes, downvotes = points
    required_points = settings.required_points
    upvote_emoji_mention = settings.upvote_emoji_mention
    downvote_emoji_mention = settings.downvote_emoji_mention
    channel = settings.channel_id
    content = message.make_link(guild_id) + "\n**"
    content += upvote_emoji_mention + "   ×" + str(upvotes)
    if downvote_emoji_mention:
        content += "   |   " + downvote_emoji_mention + "   ×" + str(downvotes)
    content += "**"
    clear_up_starboard_posts(guild_id)
    if candidate and upvotes - downvotes >= required_points:
        embed = await embedify(message, event.guild_id)
        post = await rest.create_message(
            channel,
            content,
            embed=embed
        )
        DATABASE[str(guild_id)]["Posted"][str(message.id)] = {
            "Post": post.id,
            "Timestamp": message.timestamp.timestamp(),
        }
        upvote_emoji = await settings.get_upvote_emoji()
        await rest.add_reaction(message.channel_id, message, upvote_emoji)
    if not candidate and str(message.id) in DATABASE[str(guild_id)]["Posted"]:
        post_id = DATABASE[str(guild_id)]["Posted"][str(message.id)]["Post"]
        await rest.edit_message(
            channel,
            post_id,
            content
        )

steltabulon = lightbulb.Group(
    "steltabulon", 
    "Komandoj por agordi la steltabulon por la servilo",
    default_member_permissions = hikari.Permissions.ADMINISTRATOR,
)
loader.command(steltabulon)

@steltabulon.register
class Aktivigi(
    lightbulb.SlashCommand,
    name = "aktivigi",
    description = "Agordi kaj aktivigi steltabulon",
):
    channel = lightbulb.channel(
        "steltabula_kanalo",
        "La kanalo, en kiun resendiĝu la popularaj mesaĝoj",
        channel_types=[hikari.ChannelType.GUILD_TEXT]
    )
    upvote_emoji = lightbulb.string(
        "pora_reago",
        "La emoĝio, per kiu oni povu voĉdoni por mesaĝoj"
    )
    downvote_emoji = lightbulb.string(
        "kontraŭa_reago",
        "La emoĝio, per kiu oni povu voĉdoni kontraŭ mesaĝoj",
        default=None,
    )
    required_points = lightbulb.integer(
        "havendaj_poentoj",
        "Kiom da poentoj (poraj minus kontraŭaj voĉdonoj) ricevu la mesaĝo. Implicite: " + str(REQ_POINTS_DEFAULT),
        default=REQ_POINTS_DEFAULT,
    )
    self_votes = lightbulb.integer(
        "voĉdonoj_por_si",
        "Ĉu enkalkulendu la voĉdonoj de la aŭtoro de la mesaĝo. Implicite: Ne",
        choices=BOOLEAN_CHOICES,
        default=-1,
    )
    star_blocking = lightbulb.integer(
        "blokeblo",
        "Ĉu la aŭtoro povu malpermesi ensteltabuligon per kontraŭvoĉdono. Implicite: Ne",
        choices=BOOLEAN_CHOICES,
        default=-1,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context):
        if str(ctx.guild_id) in DATABASE:
            raise UserIsWrong(
                f"En via servilo jam estas aktiva steltabulo. "
                f"Reagordu la steltabulon per «/steltabulon reagordi»"
            )
        options = {
            "channel": self.channel,
            "upvote_emoji": self.upvote_emoji,
            "downvote_emoji": self.downvote_emoji,
            "self_votes": self.self_votes,
            "star_blocking": self.star_blocking,
        }
        starboard_settings = StarboardSettings(ctx.guild_id, **options)
        embed = hikari.Embed(
            title="La agordoj de la steltabulo",
            description=starboard_settings.display_settings(),
            color=GREEN
        )
        await ctx.respond(
            f"Ci agordis la steltabulon",
            embed=embed,
            ephemeral=True,
        )

@steltabulon.register
class Reagordi(
    lightbulb.SlashCommand,
    name = "reagordi",
    description = "Reagordi la steltabulon",
):
    channel = lightbulb.channel(
        "steltabula_kanalo",
        "La kanalo, en kiun resendiĝu la popularaj mesaĝoj",
        channel_types=[hikari.ChannelType.GUILD_TEXT],
        default=None,
    )
    upvote_emoji = lightbulb.string(
        "pora_reago",
        "La emoĝio, per kiu oni povu voĉdoni por mesaĝoj",
        default=None,
    )
    downvote_emoji = lightbulb.string(
        "kontraŭa_reago",
        "La emoĝio, per kiu oni povu voĉdoni kontraŭ mesaĝoj",
        default=None,
    )
    remove_downvote_emoji = lightbulb.integer(
        "forigi_kontraŭan_reagon",
        "Ĉu forigi kontraŭan reagon, se ĝi estas agordita. Implicite: Ne",
        choices=BOOLEAN_CHOICES,
        default=None,
    )
    required_points = lightbulb.integer(
        "havendaj_poentoj",
        "Kiom da poentoj (poraj minus kontraŭaj voĉdonoj) ricevu la mesaĝo",
        default=None,
    )
    self_votes = lightbulb.integer(
        "voĉdonoj_por_si",
        "Ĉu enkalkulendu la voĉdonoj de la aŭtoro de la mesaĝo",
        choices=BOOLEAN_CHOICES,
        default=None,
    )
    star_blocking = lightbulb.integer(
        "blokeblo",
        "Ĉu la aŭtoro povu malpermesi ensteltabuligon per kontraŭvoĉdono",
        choices=BOOLEAN_CHOICES,
        default=None,
    )

    @lightbulb.invoke
    @require_confirmation(
        "**Ĉi tiu ago ne estas malfarebla.**\n"
        "Se ci ŝanĝos la steltabulan kanalon aŭ la uzeblajn emoĝiojn:\n"
        "- la jamaj steltabulaj mesaĝoj malligiĝos"
        " kaj la nombroj de la voĉdonoj pri ili ne plu aktualiĝados\n"
        "- la koncernataj mesaĝoj ne repovos ensteltabuliĝi",
    )
    async def invoke(self, ctx: lightbulb.Context):
        starboard_settings = StarboardSettings(ctx.guild_id)
        options = {
            "channel": self.channel,
            "upvote_emoji": self.upvote_emoji,
            "downvote_emoji": self.downvote_emoji,
            "required_points": self.required_points,
            "self_votes": self.self_votes,
            "star_blocking": self.star_blocking,
        }
        options = {k: v for k, v in options.items() if v}
        if self.remove_downvote_emoji:
            options["downvote_emoji"] = None
        starboard_settings.update_parameters(**options, clear_if_edited=True)
        embed = hikari.Embed(
            title="La agordoj de la steltabulo",
            description=starboard_settings.display_settings(),
            color=GREEN
        )
        await ctx.respond(
            f"Ci reagordis la steltabulon",
            embed=embed,
            ephemeral=True,
        )

@steltabulon.register
class Forigi(
    lightbulb.SlashCommand,
    name = "forigi",
    description = "Malaktivigi la steltabulon kaj forigi ĝiajn agordojn",
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context):
        if str(ctx.guild_id) not in DATABASE:
            raise UserIsWrong(f"Via servilo jam ne havas steltabulon")
        del DATABASE[str(ctx.guild_id)]
        embed = hikari.Embed(
            title="La steltabulo estas forigita",
            color=GREEN
        )
        await ctx.respond(embed=embed)

steltabulaj = lightbulb.Group("steltabulaj", "Komandoj por rigardi la steltabulajn informojn")
loader.command(steltabulaj)

@steltabulaj.register
class Informoj(
    lightbulb.SlashCommand,
    name = "informoj",
    description = "La informoj pri la steltabulaj agordoj"
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context):
        starboard_settings = StarboardSettings(ctx.guild_id)
        embed = hikari.Embed(
            title="La agordoj de la steltabulo",
            description=starboard_settings.display_settings(),
            color=GREEN
        )
        await ctx.respond(
            embed=embed,
            ephemeral=True,
        )

# def load(bot: lightbulb.BotApp):
#     bot.add_plugin(loader)

# def unload(bot: lightbulb.BotApp):
#     bot.remove_plugin(loader)
