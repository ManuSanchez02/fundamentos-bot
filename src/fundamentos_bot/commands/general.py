from discord import app_commands, Interaction

from fundamentos_bot.commands.base_cog import BaseCog


class General(BaseCog):
    """General commands for the bot.
    This class contains general commands that do not fit into other categories.
    """

    @app_commands.command(name="ping", description="Ping the bot")
    async def ping(self, interaction: Interaction):
        """A simple slash command that responds with 'Pong!'"""
        await interaction.response.send_message("Pong!", ephemeral=True)
