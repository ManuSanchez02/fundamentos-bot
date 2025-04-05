import discord
from discord.ext import commands

from algo1_bot.commands.general import General

import logging

from algo1_bot.commands.spreadsheet import Spreadsheet
from algo1_bot.config import Config

BOT_PREFIX = "!"

logger = logging.getLogger(__name__)


class MyBot(commands.Bot):
    def __init__(self, config: Config):
        super().__init__(command_prefix=BOT_PREFIX, intents=discord.Intents.default())
        self.config = config

    async def setup_hook(self):
        """Load all Cogs (commands) on startup"""
        await self.add_cog(General(self))
        await self.add_cog(Spreadsheet(self, self.config.spreadsheet_id))
        await self.tree.sync()
        logger.info("Slash commands synced!")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def process_commands(self, _message):
        pass
