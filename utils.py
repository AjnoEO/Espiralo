from typing import Callable
from functools import wraps
import hikari
import lightbulb
import lightbulb.context
import miru
from discord_emojis import EMOJIS
import re
from configparser import ConfigParser
from utils_eo import get_color

class UserIsWrong(Exception):
    """Erarklaso por eraroj, kiujn povas kaŭzi misagoj de la uzantoj"""

config = ConfigParser()
config.read("config.ini")
data = config["datumoj"]
OWNER = int(data["posedanto"])

@lightbulb.hook(lightbulb.ExecutionSteps.CHECKS)
async def owner_only(_: lightbulb.ExecutionPipeline, ctx: lightbulb.Context) -> None:
    """Instrukcio por permesi komandon nur por la robotestro"""
    command_name = ctx.command_data.name
    if ctx.command_data.type == hikari.CommandType.SLASH:
        command_name = "/" + command_name
    if ctx.user.id != OWNER:
        raise UserIsWrong(f"Nur <@{OWNER}> rajtas uzi la komandon `{command_name}`")

class ConfirmationButton(miru.Button):
    def __init__(self, label: str, style: hikari.ButtonStyle, value) -> None:
        super().__init__(label, style=style)
        self.view: Confirmation
        self.value = value

    async def callback(self, _: miru.ViewContext) -> None:
        self.view.confirmed = self.value
        self.view.stop()

class Confirmation(miru.View):
    def __init__(self, confirm: str, cancel: str) -> None:
        super().__init__()
        self.confirmed: bool | None = None
        self.add_item(ConfirmationButton(confirm, style=hikari.ButtonStyle.SECONDARY, value=True))
        self.add_item(ConfirmationButton(cancel, style=hikari.ButtonStyle.PRIMARY, value=False))

def require_confirmation(
    warning_description: str | None,
    *,
    warning_title: str = "Ĉu ci certas?",
    confirm: str = "Konfirmi",
    cancel: str = "Nuligi",
    color: str = get_color("Ruĝo"),
):
    def decorator(func: Callable):
        @wraps(func)
        @lightbulb.di.with_di
        async def wrapper(self_: lightbulb.CommandBase, ctx: lightbulb.Context, mc: miru.Client = lightbulb.di.INJECTED) -> None:

            embed = hikari.Embed(
                title=warning_title,
                description=warning_description,
                color=color,
            )
            view = Confirmation(confirm, cancel)

            confirmation_response_id = await ctx.respond(embed, components=view, ephemeral=True)
            mc.start_view(view)
            await view.wait()

            await ctx.delete_response(confirmation_response_id)
            if view.confirmed:
                await func(self_, ctx)

        return wrapper
    return decorator

async def get_author_member(message: hikari.Message, guild_id: int) -> hikari.Member:
    if message.member:
        return message.member
    if not guild_id:
        return None
    app: hikari.GatewayBot = message.app
    author = app.cache.get_member(guild_id, message.author.id)
    if author:
        return author
    return await app.rest.fetch_member(guild_id, message.author.id)

def check_emoji(string: str) -> int | str:
    string = string.strip()
    if match := re.match(r"<:\w+:(\d+)>$", string):
        return int(match.group(1))
    if string in EMOJIS:
        return string
    raise ValueError(f"{string} ne estas valida emoĝio")

def string_from_emoji(emoji: hikari.Emoji | str | None) -> str | None:
    if not emoji:
        return None
    if isinstance(emoji, hikari.CustomEmoji):
        return emoji.mention
    if isinstance(emoji, hikari.UnicodeEmoji):
        return emoji.name
    if check_emoji(emoji):
        return emoji

async def emoji_from_string(string: str, guild_id: int, rest: hikari.api.RESTClient) -> hikari.Emoji:
    """La identigilo de aldonita emoĝio, aŭ la unikoda emoĝio"""
    emoji = check_emoji(string)
    if isinstance(emoji, int):
        return await rest.fetch_emoji(guild_id, emoji)
    return hikari.UnicodeEmoji(string)

@lightbulb.di.with_di
async def author_reacted(message: hikari.Message, emoji: hikari.Emoji, rest: hikari.api.RESTClient = lightbulb.di.INJECTED):
    reacted_list = rest.fetch_reactions_for_emoji(message.channel_id, message.id, emoji)
    async for user in reacted_list:
        if user == message.author:
            return True
    return False

def strif(value: bool, string: str) -> str:
    return string if value else ""

def main():
    ...

if __name__ == "__main__":
    main()