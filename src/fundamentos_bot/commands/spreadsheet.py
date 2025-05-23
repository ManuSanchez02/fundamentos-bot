from typing import override
from discord import app_commands, Interaction
import logging

from fundamentos_bot.commands.base_cog import BaseCog
from fundamentos_bot.gcp import SpreadsheetManager, TokenManager
from fundamentos_bot.gcp.spreadsheet_manager import Schema

SPREADSHEET_NAME = "Alumnos"
START_ROW = 2
START_COL = "A"
END_COL = "E"
EMAIL_COL = "D"

logger = logging.getLogger(__name__)


class StudentSchema(Schema):
    """Schema for the student data in the spreadsheet."""

    full_name: str
    student_id: int
    practice_class: str
    email: str

    @override
    @classmethod
    def from_row(cls, row: list[str]):
        """
        Converts a row from the spreadsheet into a dictionary.

        Args:
            row: A list of strings representing a row in the spreadsheet.

        Returns:
            - student: An instance of StudentSchema with the data from the row.
        """
        return cls(
            full_name=row[0],
            student_id=int(row[1]),
            practice_class=row[2],
            email=row[3],
        )


class Spreadsheet(BaseCog):
    """Spreadsheet commands for the bot.
    This class contains commands that interact with the Google Sheets API.

    Attributes:
        bot: The bot instance.
        spreadsheet_manager: The manager for handling spreadsheet operations.
    """

    def __init__(self, bot, spreadsheet_id: str):
        """Initialize the Spreadsheet cog.

        Args:
            bot: The bot instance.
            spreadsheet_id: The ID of the Google Spreadsheet to interact with.
        """
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
        if email_actual == nuevo_email:
            await interaction.response.send_message(
                "El nuevo email es el mismo que el actual", ephemeral=True
            )
            return

        logger.info(f"Received email change request for {padron} to {nuevo_email}")
        await interaction.response.defer(thinking=True, ephemeral=True)
        target_range = f"{SPREADSHEET_NAME}!{START_COL}{START_ROW}:{END_COL}"
        data = await self.spreadsheet_manager.get_range(
            target_range, schema=StudentSchema
        )
        students = data.values
        found_index = None
        for i, student in enumerate(students, START_ROW):
            if student.student_id == padron and student.email == email_actual:
                logger.debug(
                    f"Found student {padron} with email {email_actual}, updating to {nuevo_email}"
                )
                found_index = i
                break
        else:
            await interaction.followup.send(
                f"No se encontró el padrón {padron} o el email actual no coincide"
            )
            return

        cell_to_update = f"{EMAIL_COL}{found_index}:{EMAIL_COL}{found_index}"
        logger.debug(f"Updating cell {cell_to_update} with new email {nuevo_email}")
        await self.spreadsheet_manager.update_range(
            target_range=cell_to_update,
            values=[[nuevo_email]],
        )
        logger.info(
            f"Successfully updated email for {padron} from {email_actual} to {nuevo_email}"
        )
        await interaction.followup.send(
            f"Se actualizó el email del alumno con padrón {padron} a {nuevo_email}"
        )
