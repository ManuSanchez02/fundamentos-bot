import discord
from discord.ext import commands

from algo1_bot.commands.general import General

import logging

from algo1_bot.commands.spreadsheet import Spreadsheet

logger = logging.getLogger(__name__)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=None, intents=discord.Intents.default()
        )  # Slash commands only

    async def setup_hook(self):
        """Load all Cogs (commands) on startup"""
        await self.add_cog(General(self))
        await self.add_cog(Spreadsheet(self))
        await self.tree.sync()
        logger.info("Slash commands synced!")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def process_commands(self, _message):
        pass
