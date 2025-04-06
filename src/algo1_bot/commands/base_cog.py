from discord.ext.commands import Cog


class BaseCog(Cog):
    """
    Base class for all cogs in the bot.
    This class provides a common interface for all cogs, it should not be used directly.
    All cogs should inherit from this class.

    Attributes:
        bot: The bot instance.
    """

    def __init__(self, bot):
        """Initialize the cog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot
