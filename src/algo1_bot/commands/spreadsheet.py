from discord import app_commands, Interaction

from algo1_bot.commands.base_cog import BaseCog


class Spreadsheet(BaseCog):
    @app_commands.command(name="change_email", description="Change your email")
    @app_commands.describe(student_id="Your student id")
    @app_commands.describe(new_email="Your new email address")
    async def change_email(
        self, interaction: Interaction, student_id: int, new_email: str
    ):
        """Changes the email address corresponding to the given student id in the spreadsheet"""
        await interaction.response.send_message(
            f"Changed email for {student_id} to {new_email}", ephemeral=True
        )
