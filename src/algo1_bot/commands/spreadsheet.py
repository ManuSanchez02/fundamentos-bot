from discord import app_commands, Interaction

from algo1_bot.commands.base_cog import BaseCog
from algo1_bot.gcp import SpreadsheetManager, TokenManager

RANGE = "Alumnos!A2:E"


# class StudentRecord:
#     def __init__(self, student_id: int, email: str):
#         self.student_id = student_id
#         self.email = email

#     def __repr__(self):
#         return f"StudentRecord(student_id={self.student_id}, email='{self.email}')"

#     def to_dict(self):
#         return {
#             "student_id": self.student_id,
#             "email": self.email,
#         }


class Spreadsheet(BaseCog):
    def __init__(self, bot, spreadsheet_id: str):
        super().__init__(bot)
        token_manager = TokenManager()
        self.spreadsheet_manager = SpreadsheetManager(
            token_manager=token_manager,
            spreadsheet_id=spreadsheet_id,
        )

    @app_commands.command(name="cambiar_email", description="Cambia tu email")
    @app_commands.describe(padron="Tu numero de padrón o legajo")
    @app_commands.describe(email_actual="Tu email actual")
    @app_commands.describe(nuevo_email="Tu nuevo email")
    async def change_email(
        self, interaction: Interaction, padron: int, email_actual: str, nuevo_email: str
    ):
        """Changes the email address corresponding to the given student id in the spreadsheet"""
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.spreadsheet_manager.get_data(RANGE)
        _values = data.values

        await interaction.followup.send(f"Changed email for {padron} to {nuevo_email}")
