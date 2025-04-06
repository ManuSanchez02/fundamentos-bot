"""
This script provides a class to manage a Google Sheets spreadsheet.
It fetches data from the spreadsheet using the Google Sheets API.
For more details, see: https://developers.google.com/workspace/sheets/api/reference/rest
"""

from dataclasses import dataclass
import aiohttp
import logging

from algo1_bot.gcp.token_manager import TokenManager

SPREADSHEETS_BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"

logger = logging.getLogger(__name__)


@dataclass
class SpreadsheetData:
    range: str
    major_dimension: str
    values: list[list[str]]


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

    async def get_data(self, range: str) -> SpreadsheetData:
        logger.debug(
            f"Fetching data from range: {range} in spreadsheet: {self.spreadsheet_id}"
        )
        token = await self.token_manager.get_token()
        return await _fetch_data(token, self.spreadsheet_id, range)
