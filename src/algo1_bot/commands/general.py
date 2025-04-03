import discord
from discord import app_commands

from algo1_bot.commands.base_cog import BaseCog


class General(BaseCog):
    @app_commands.command(name="hello", description="Say hello!")
    async def hello(self, interaction: discord.Interaction):
        """A simple slash command"""
        await interaction.response.send_message(f"Hi, {interaction.user.mention}!")
