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

from fundamentos_bot.gcp.token_manager import TokenManager

SPREADSHEETS_BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"
VALUE_INPUT_OPTION = "USER_ENTERED"

logger = logging.getLogger(__name__)


class Schema(ABC, BaseModel):
    """Base class for schema representation of spreadsheet data.
    This class should be subclassed to define specific schemas for different
    spreadsheet data structures."""

    @classmethod
    def from_row(cls, row: list[str]) -> Self:
        """
        Converts a row from the spreadsheet into a dictionary.
        This method should be overridden in subclasses to provide custom mapping.

        Args:
            row: A list of strings representing a row in the spreadsheet.

        Returns:
            parsed_row: An instance of the subclass with the data from the row.
        """
        raise NotImplementedError("Subclasses must implement this method.")


T = TypeVar("T", bound=Schema)


@dataclass
class _BaseSpreadsheetData:
    """Base class for spreadsheet data representation.
    This class contains common attributes for all spreadsheet data types.

    Attributes:
        target_range: The range of the spreadsheet data.
        major_dimension: The major dimension of the data (ROWS or COLUMNS).
    """

    target_range: str
    major_dimension: str


@dataclass
class _RawSpreadsheetData(_BaseSpreadsheetData):
    """Class for raw spreadsheet data representation.
    This class contains the raw values fetched from the spreadsheet.

    Attributes:
        target_range: The range of the spreadsheet data.
        major_dimension: The major dimension of the data (ROWS or COLUMNS).
        values: A list of raw values fetched from the spreadsheet."""

    values: list[list[str]]


@dataclass
class SpreadsheetData(_BaseSpreadsheetData, Generic[T]):
    """Class for structured spreadsheet data representation.
    This class contains the structured values parsed from the raw data.

    Attributes:
        target_range: The range of the spreadsheet data.
        major_dimension: The major dimension of the data (ROWS or COLUMNS).
        values: A list of parsed values, where each value is an instance of the schema."""

    values: list[T]


async def _get_data(
    token: str, spreadsheet_id: str, target_range: str
) -> _RawSpreadsheetData:
    """Fetches data from the specified range in the spreadsheet.

    Args:
        token: The access token for authentication.
        spreadsheet_id: The ID of the spreadsheet to fetch data from.
        target_range: The range of cells to fetch data from.

    Returns:
        data: An instance of _RawSpreadsheetData containing the fetched data.

    Raises:
        aiohttp.ClientError: If there is an error with the HTTP request.
        KeyError: If the response does not contain the expected keys.
        ValueError: If the response cannot be parsed as JSON.
    """
    url = f"{SPREADSHEETS_BASE_URL}/{spreadsheet_id}/values/{target_range}"

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            logger.debug(f"Successfully got data: {response_data}")

    try:
        return _RawSpreadsheetData(
            target_range=response_data["range"],
            major_dimension=response_data["majorDimension"],
            values=response_data["values"],
        )
    except KeyError as e:
        logger.error(f"Invalid get data response: {response_data}")
        raise KeyError(
            f"Missing key in response data: {e}. Please check the API response."
        )


async def _update_data(
    token: str, spreadsheet_id: str, target_range: str, values: list[list[str]]
) -> None:
    """Updates the specified range in the spreadsheet with the provided values.

    Args:
        token: The access token for authentication.
        spreadsheet_id: The ID of the spreadsheet to update.
        target_range: The range of cells to update.
        values: A list of lists containing the values to update.

    Raises:
        aiohttp.ClientError: If there is an error with the HTTP request.
        ValueError: If the response cannot be parsed as JSON.
    """
    if len(values) == 0:
        logger.warning("No values provided for update.")
        return

    url = f"{SPREADSHEETS_BASE_URL}/{spreadsheet_id}/values/{target_range}?valueInputOption={VALUE_INPUT_OPTION}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "range": target_range,
        "majorDimension": "ROWS" if len(values) <= len(values[0]) else "COLUMNS",
        "values": values,
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=body) as response:
            response.raise_for_status()
            response_data = await response.json()
            logger.debug(f"Successfully updated data: {response_data}")


class SpreadsheetManager:
    """Class to manage a Google Sheets spreadsheet.
    This class provides methods to fetch and update data in the spreadsheet.

    Attributes:
        token_manager: An instance of TokenManager to handle authentication.
        spreadsheet_id: The ID of the spreadsheet to manage.
    """

    def __init__(self, token_manager: TokenManager, spreadsheet_id: str):
        """Initialize the SpreadsheetManager with the given token manager and spreadsheet ID.

        Args:
            token_manager: An instance of TokenManager to handle authentication.
            spreadsheet_id: The ID of the spreadsheet to manage.
        """
        self.token_manager = token_manager
        self.spreadsheet_id = spreadsheet_id

    async def get_range(self, target_range: str, schema: Type[T]) -> SpreadsheetData[T]:
        """Gets data from the specified range in the spreadsheet and parses it using the provided schema.

        Args:
            target_range: The range of cells to fetch data from.
            schema: A subclass of Schema to parse the fetched data.

        Returns:
            data: An instance of SpreadsheetData containing the parsed data.

        Raises:
            aiohttp.ClientError: If there is an error with the HTTP request.
            KeyError: If the response does not contain the expected keys.
            ValueError: If the response cannot be parsed as JSON.
        """
        logger.debug(
            f"Getting data from range: {target_range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        data = await _get_data(token, self.spreadsheet_id, target_range)
        values = [schema.from_row(row) for row in data.values]

        return SpreadsheetData(
            target_range=data.target_range,
            major_dimension=data.major_dimension,
            values=values,
        )

    async def update_range(self, target_range: str, values: list[list[str]]):
        """Updates the specified range in the spreadsheet with the provided values.

        Args:
            target_range: The range of cells to update.
            values: A list of lists containing the values to update.

        Raises:
            aiohttp.ClientError: If there is an error with the HTTP request.
            ValueError: If the response cannot be parsed as JSON.
        """
        logger.debug(
            f"Updating data in range: {target_range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        await _update_data(token, self.spreadsheet_id, target_range, values)
