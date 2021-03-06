import traceback
import discord
import uvloop
from modules import logger as log, maria, helpcommand
from modules.config import Config
from discord.ext import commands
from time import time

uvloop.install()
logger = log.get_logger(__name__)

intents = discord.Intents(
    guilds=True,
    members=False,  # requires verification
    bans=False,
    emojis=False,
    integrations=False,
    webhooks=False,
    invites=False,
    voice_states=False,
    presences=False,  # requires verification
    guild_messages=True,
    guild_reactions=True,
    typing=False,
)

extensions = ["cogs.events", "cogs.commands", "cogs.errorhandler", "cogs.streamer"]


class FansiteBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        self.config = Config("config.toml")
        super().__init__(
            command_prefix=self.config.prefix, owner_id=self.config.owner_id, **kwargs
        )
        self.logger = logger
        self.start_time = time()
        self.twitter_blue = int("1da1f2", 16)
        self.db = maria.MariaDB(self)

    async def close(self):
        await self.db.cleanup()
        await super().close()

    async def on_message(self, message):
        if not bot.is_ready:
            return

        await super().on_message(message)


bot = FansiteBot(
    case_insensitive=True,
    help_command=helpcommand.EmbedHelpCommand(),
    allowed_mentions=discord.AllowedMentions(everyone=False),
    description="Bot for following twitter users on discord",
    intents=intents,
)


@bot.before_invoke
async def before_any_command(ctx):
    """Runs before any command."""
    ctx.time = time()
    try:
        await ctx.trigger_typing()
    except discord.errors.Forbidden:
        pass


def run(bot):
    """Load extensions and run the bot."""
    for extension in extensions:
        try:
            bot.load_extension(extension)
            bot.logger.info(f"Imported {extension}")
        except Exception as error:
            bot.logger.error(f"Error loading {extension} , aborting")
            traceback.print_exception(type(error), error, error.__traceback__)
            quit()

    bot.logger.info("All extensions loaded successfully")
    bot.run(bot.config.discord_token)


if __name__ == "__main__":
    run(bot)
