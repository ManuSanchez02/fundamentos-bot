"""
This script provides a class to manage a Google Sheets spreadsheet.
It fetches data from the spreadsheet using the Google Sheets API.
"""

from dataclasses import dataclass
import aiohttp

from algo1_bot.gcp.token_manager import TokenManager

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"


@dataclass
class SpreadsheetData:
    range: str
    major_dimension: str
    values: list[list[str]]


async def _fetch_data(token: str, spreadsheet_id: str, range: str) -> SpreadsheetData:
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range}"
    )

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()

    try:
        return SpreadsheetData(
            range=response_data["range"],
            major_dimension=response_data["majorDimension"],
            values=response_data["values"],
        )
    except KeyError as e:
        raise KeyError(
            f"Missing key in response data: {e}. Please check the API response."
        )


class SpreadsheetManager:
    def __init__(self, token_manager: TokenManager, spreadsheet_id: str):
        self.token_manager = token_manager
        self.spreadsheet_id = spreadsheet_id

    async def get_data(self, range: str) -> SpreadsheetData:
        token = await self.token_manager.get_token()
        return await _fetch_data(token, self.spreadsheet_id, range)
