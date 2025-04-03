from discord import app_commands, Interaction

from algo1_bot.commands.base_cog import BaseCog


class General(BaseCog):
    @app_commands.command(name="ping", description="Ping the bot")
    async def ping(self, interaction: Interaction):
        """A simple slash command that responds with 'Pong!'"""
        await interaction.response.send_message("Pong!", ephemeral=True)
