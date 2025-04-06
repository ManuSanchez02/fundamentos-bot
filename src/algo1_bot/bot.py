"""Bot module for the Discord bot.
This module contains the MyBot class, which is a subclass of discord.ext.commands.Bot."""

from discord import Intents, Object
from discord.ext import commands

from algo1_bot.commands.general import General

import logging

from algo1_bot.commands.spreadsheet import Spreadsheet
from algo1_bot.config import Config

BOT_PREFIX = "!"

logger = logging.getLogger(__name__)


class FundamentosBot(commands.Bot):
    """Discord bot class that handles commands and events.
    This class is a subclass of discord.ext.commands.Bot and is responsible for
    setting up the bot, loading cogs, and handling events.

    Attributes:
        config: Configuration object containing bot settings.
    """

    def __init__(self, config: Config):
        """Initialize the bot with the given configuration.

        Args:
            config: Configuration object containing bot settings.
        """
        super().__init__(command_prefix=BOT_PREFIX, intents=Intents.default())
        self.config = config

    async def setup_hook(self):
        """Load all Cogs (commands) on startup"""
        guild = None
        if self.config.guild_id:
            guild = Object(id=self.config.guild_id)
            logger.info(f"Guild ID: {self.config.guild_id}")
        await self.add_cog(General(self))
        await self.add_cog(Spreadsheet(self, self.config.spreadsheet_id))
        if guild:
            self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info("Slash commands synced!")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def process_commands(self, _message):
        """Process messages that match the command prefix."""
        # This method is intentionally left blank in order to only process slash commands.
        pass
