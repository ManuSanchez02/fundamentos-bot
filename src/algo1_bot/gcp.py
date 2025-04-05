"""
This script generates an access token to use in the Google Sheets API.
For more details, see: https://developers.google.com/identity/protocols/oauth2/service-account#httprest
"""

import jwt
from datetime import datetime
import aiohttp
import json

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"

RANGE = "Alumnos!A2:E"


with open("./gcp_credentials.json") as f:
    data = json.load(f)
    private_key = data["private_key"]
    issuer = data["client_email"]


def encode_jwt():
    current_time = int(datetime.now().timestamp())
    return jwt.encode(
        {
            "iss": issuer,
            "scope": SCOPE,
            "aud": TOKEN_URL,
            "iat": current_time,
            "exp": current_time + ACCESS_TOKEN_DURATION,
        },
        key=private_key,
        algorithm=JWT_ENCRYPTION_ALGORITHM,
        headers={
            "alg": JWT_ENCRYPTION_ALGORITHM,
            "typ": "JWT",
        },
    )


async def async_get_token(encoded_jwt: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TOKEN_URL,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": encoded_jwt,
            },
        ) as response:
            return await response.json()


async def fetch_data(token: str, spreadsheet_id: str, range: str):
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range}"
    )

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            print(data["values"])


async def main():
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    encoded_jwt = encode_jwt()
    token_response = await async_get_token(encoded_jwt)
    access_token = token_response["access_token"]
    await fetch_data(access_token, spreadsheet_id, RANGE)


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import os

    load_dotenv()

    token = asyncio.run(main())
