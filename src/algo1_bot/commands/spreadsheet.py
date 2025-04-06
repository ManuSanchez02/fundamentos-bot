from typing import override
from discord import app_commands, Interaction
import logging

from algo1_bot.commands.base_cog import BaseCog
from algo1_bot.gcp import SpreadsheetManager, TokenManager
from algo1_bot.gcp.spreadsheet_manager import Schema

SPREADSHEET_NAME = "Alumnos"
START_ROW = 2
START_COL = "A"
END_COL = "E"
EMAIL_COL = "D"

logger = logging.getLogger(__name__)


class StudentSchema(Schema):
    full_name: str
    student_id: int
    practice_class: str
    email: str

    @override
    @classmethod
    def from_row(cls, row: list[str]):
        """
        Converts a row from the spreadsheet into a dictionary.
        This method should be overridden in subclasses to provide custom mapping.
        """
        return cls(
            full_name=row[0],
            student_id=int(row[1]),
            practice_class=row[2],
            email=row[3],
        )


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
        if email_actual == nuevo_email:
            await interaction.response.send_message(
                "El nuevo email es el mismo que el actual", ephemeral=True
            )
            return

        logger.info(f"Received email change request for {padron} to {nuevo_email}")
        await interaction.response.defer(thinking=True, ephemeral=True)
        range = f"{SPREADSHEET_NAME}!{START_COL}{START_ROW}:{END_COL}"
        data = await self.spreadsheet_manager.get_range(range, schema=StudentSchema)
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
            range=cell_to_update,
            values=[[nuevo_email]],
        )
        logger.info(
            f"Successfully updated email for {padron} from {email_actual} to {nuevo_email}"
        )
        await interaction.followup.send(
            f"Se actualizó el email de {padron} a {nuevo_email}"
        )
