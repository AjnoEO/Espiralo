"""La ĉefprogramo"""

from configparser import ConfigParser
import os
import hikari
import lightbulb
import miru
import re
from utils import require_confirmation, UserIsWrong, owner_only
from utils_eo import get_color

config = ConfigParser()
config.read("config.ini")

data = config["datumoj"]
TOKEN = data["jxetono"]
SUPPORT_SERVER = data["servila_invitligilo"]
TEST_SERVER_ID = int(data["testservila_identigilo"])

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS | hikari.Intents.GUILD_PRESENCES

EXTENSIONS = [
    "steltabulo"
]
RED = get_color("Ruĝo")

bot = hikari.GatewayBot(
    token=TOKEN,
    # help_class=None,
    logs="INFO",
    intents=INTENTS,
)
lightbulb_client = lightbulb.client_from_app(bot)
miru_client = miru.Client(bot)
lightbulb_client.di.registry_for(
    lightbulb.di.Contexts.DEFAULT
).register_value(miru.Client, miru_client)

@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    await lightbulb_client.load_extensions(*EXTENSIONS)
    await lightbulb_client.start()

@lightbulb_client.error_handler
async def handler(exc: lightbulb.exceptions.ExecutionPipelineFailedException) -> bool:
    """Erartraktilo"""
    handled = False
    if exc.pipeline.invocation_failed:
        error_cause = exc.invocation_failure
    else:
        error_cause = exc.hook_failures[0]
    if isinstance(error_cause, UserIsWrong):
        error_message = str(error_cause)
        handled = True
    else:
        traceback = error_cause.__traceback__
        while traceback.tb_next:
            traceback = traceback.tb_next
        filename = os.path.split(traceback.tb_frame.f_code.co_filename)[1]
        line_number = traceback.tb_lineno
        error_name = error_cause.__class__.__name__
        command_name = exc.context.command_data.name
        if exc.context.command_data.type == hikari.CommandType.SLASH:
            command_name = "/" + command_name
        error_message = (
            f"Okazis eraro dum plenumado de `{command_name}`.\n"
            f"La erarmesaĝo: "
            f"`{error_name} ({filename}, linio {line_number}): {error_cause}`"
        )
    embed = hikari.Embed(
        title="Eraro!",
        description=(
            f"{error_message}\n\n"
            f"Se ci opinias tion cimo, raportu la eraron ĉe "
            f"[la servilo de la roboto]({SUPPORT_SERVER})"
        ),
        color=RED
    )
    await exc.context.respond(embed, ephemeral=True)
    return handled

class HelloButtons(miru.View):
    
    @miru.button(label="Saluton!", emoji="👋", style=hikari.ButtonStyle.SUCCESS)
    async def button_good(self, ctx: miru.ViewContext, _: miru.Button) -> None:
        ctx.view.stop()
        await ctx.edit_response(":D", components=None)

    @miru.button(label="Iru kacen!", style=hikari.ButtonStyle.DANGER)
    async def button_bad(self, ctx: miru.ViewContext, _: miru.Button) -> None:
        ctx.view.stop()
        await ctx.edit_response(":c", components=None)

@lightbulb_client.register
class Saluti(
    lightbulb.SlashCommand,
    name = "saluti",
    description = "Diri saluton!",
    hooks = [owner_only],
):
    @require_confirmation(None)
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context, miru_client: miru.Client = lightbulb.di.INJECTED) -> None:
        view = HelloButtons()
        await ctx.respond("Saluton!", components=view, ephemeral=True)
        miru_client.start_view(view)


@lightbulb_client.register
class Diri(
    lightbulb.SlashCommand,
    name = "diri",
    description = "Diri ion nome de la roboto",
    hooks = [owner_only],
):
    message = lightbulb.string("mesaĝon", "La direnda mesaĝo")
    channel = lightbulb.channel(
        "en-kanalon",
        "La kanalo, en kiun sendendas la mesaĝo",
        channel_types=[hikari.ChannelType.GUILD_TEXT],
        default=None,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        channel = self.channel.id if self.channel else ctx.channel_id
        await bot.rest.create_message(channel, self.message)
        response = "Mi sendis la mesaĝon"
        if self.channel:
            response += f" en la kanalon {self.channel.mention}"
        await ctx.respond(
            response,
            ephemeral=True
        )

@lightbulb_client.register(guilds = [TEST_SERVER_ID])
class Resxargi(
    lightbulb.SlashCommand,
    name = "reŝargi",
    description = "Reŝargi kromprogramon de la roboto",
    default_member_permissions = hikari.Permissions.ADMINISTRATOR,
    hooks = [owner_only],
):
    extension = lightbulb.string(
        "kromprogramon",
        "La reŝargenda kromprogramo",
        choices=[lightbulb.Choice(name=e, value=e) for e in EXTENSIONS]
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        extension = self.extension
        await lightbulb_client.reload_extensions(extension)
        await ctx.respond(
            f"Mi reŝargis la kromprogramon {extension}",
            ephemeral=True
        )

bot.run()
