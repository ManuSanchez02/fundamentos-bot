"""
This script provides a class to manage a Google Sheets spreadsheet.
It fetches data from the spreadsheet using the Google Sheets API.
For more details, see: https://developers.google.com/workspace/sheets/api/reference/rest
"""

from dataclasses import dataclass
from typing import Generic, Self, Type, TypeVar
import aiohttp
import logging
from abc import ABC

from pydantic import BaseModel

from algo1_bot.gcp.token_manager import TokenManager

SPREADSHEETS_BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"
VALUE_INPUT_OPTION = "USER_ENTERED"

logger = logging.getLogger(__name__)


class Schema(ABC, BaseModel):
    @classmethod
    def from_row(cls, row: list[str]) -> Self:
        """
        Converts a row from the spreadsheet into a dictionary.
        This method should be overridden in subclasses to provide custom mapping.
        """
        raise NotImplementedError("Subclasses must implement this method.")


T = TypeVar("T", bound=Schema)


@dataclass
class _BaseSpreadsheetData:
    range: str
    major_dimension: str


@dataclass
class _RawSpreadsheetData(_BaseSpreadsheetData):
    values: list[list[str]]


@dataclass
class SpreadsheetData(_BaseSpreadsheetData, Generic[T]):
    values: list[T]


async def _get_data(token: str, spreadsheet_id: str, range: str) -> _RawSpreadsheetData:
    url = f"{SPREADSHEETS_BASE_URL}/{spreadsheet_id}/values/{range}"

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            logger.debug(f"Successfully got data: {response_data}")

    try:
        return _RawSpreadsheetData(
            range=response_data["range"],
            major_dimension=response_data["majorDimension"],
            values=response_data["values"],
        )
    except KeyError as e:
        logger.error(f"Invalid get data response: {response_data}")
        raise KeyError(
            f"Missing key in response data: {e}. Please check the API response."
        )


async def _update_data(
    token: str, spreadsheet_id: str, range: str, values: list[list[str]]
) -> None:
    if len(values) == 0:
        logger.warning("No values provided for update.")
        return

    url = f"{SPREADSHEETS_BASE_URL}/{spreadsheet_id}/values/{range}?valueInputOption={VALUE_INPUT_OPTION}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "range": range,
        "majorDimension": "ROWS" if len(values) < len(values[0]) else "COLUMNS",
        "values": values,
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=body) as response:
            response.raise_for_status()
            response_data = await response.json()
            logger.debug(f"Successfully updated data: {response_data}")


class SpreadsheetManager:
    def __init__(self, token_manager: TokenManager, spreadsheet_id: str):
        self.token_manager = token_manager
        self.spreadsheet_id = spreadsheet_id

    async def get_range(self, range: str, schema: Type[T]) -> SpreadsheetData[T]:
        logger.debug(
            f"Fetching data from range: {range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        data = await _get_data(token, self.spreadsheet_id, range)
        values = [schema.from_row(row) for row in data.values]

        return SpreadsheetData(
            range=data.range,
            major_dimension=data.major_dimension,
            values=values,
        )

    async def update_range(self, range: str, values: list[list[str]]):
        logger.debug(
            f"Updating data in range: {range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        await _update_data(token, self.spreadsheet_id, range, values)
