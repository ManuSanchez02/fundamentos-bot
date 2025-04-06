"""
This script provides a class to manage a Google Sheets spreadsheet.
It fetches data from the spreadsheet using the Google Sheets API.
For more details, see: https://developers.google.com/workspace/sheets/api/reference/rest
"""

from dataclasses import dataclass
from typing import Self
import aiohttp
import logging
from abc import ABC

from algo1_bot.gcp.token_manager import TokenManager

SPREADSHEETS_BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"

logger = logging.getLogger(__name__)


class Schema(ABC):
    @classmethod
    def from_row(cls, row: list[str]) -> Self:
        """
        Converts a row from the spreadsheet into a dictionary.
        This method should be overridden in subclasses to provide custom mapping.
        """
        raise NotImplementedError("Subclasses must implement this method.")


@dataclass
class BaseSpreadsheetData:
    range: str
    major_dimension: str


@dataclass
class SpreadsheetData(BaseSpreadsheetData):
    values: list[list[str]]


@dataclass
class ParsedSpreadsheetData(BaseSpreadsheetData):
    values: list[Schema]


async def _fetch_data(token: str, spreadsheet_id: str, range: str) -> SpreadsheetData:
    url = f"{SPREADSHEETS_BASE_URL}/{spreadsheet_id}/values/{range}"

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            logger.debug(f"Successfully fetched data: {response_data}")

    try:
        return SpreadsheetData(
            range=response_data["range"],
            major_dimension=response_data["majorDimension"],
            values=response_data["values"],
        )
    except KeyError as e:
        logger.error(f"Invalid fetch data response: {response_data}")
        raise KeyError(
            f"Missing key in response data: {e}. Please check the API response."
        )


class SpreadsheetManager:
    def __init__(self, token_manager: TokenManager, spreadsheet_id: str):
        self.token_manager = token_manager
        self.spreadsheet_id = spreadsheet_id

    async def get_data(
        self, range: str, schema: Schema | None = None
    ) -> SpreadsheetData | ParsedSpreadsheetData:
        logger.debug(
            f"Fetching data from range: {range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        data = await _fetch_data(token, self.spreadsheet_id, range)
        values = data.values
        if not schema or len(values) == 0:
            return data

        parsed_values = [schema.from_row(row) for row in values]

        return ParsedSpreadsheetData(
            range=data.range,
            major_dimension=data.major_dimension,
            values=parsed_values,
        )
