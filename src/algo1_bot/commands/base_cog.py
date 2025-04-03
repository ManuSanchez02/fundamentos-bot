from discord.ext.commands import Cog


class BaseCog(Cog):
    """
    Base class for all cogs in the bot.
    """

    def __init__(self, bot):
        self.bot = bot
