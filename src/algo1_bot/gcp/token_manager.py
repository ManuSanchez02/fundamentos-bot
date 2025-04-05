"""
This script generates an access token to use in the Google Sheets API.
For more details, see: https://developers.google.com/identity/protocols/oauth2/service-account#httprest
"""

import asyncio
from dataclasses import dataclass
import jwt
from datetime import datetime, timedelta
import aiohttp
import json

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"


@dataclass
class TokenResponse:
    access_token: str
    expires_in: int


async def _async_get_token(encoded_jwt: str) -> TokenResponse:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TOKEN_URL,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": encoded_jwt,
            },
        ) as response:
            response.raise_for_status()
            token_response = await response.json()

    try:
        token = token_response["access_token"]
        expires_in = int(token_response["expires_in"])
    except KeyError:
        raise KeyError("Invalid token response. Please check your credentials.")
    except ValueError:
        raise ValueError("Invalid token response. Could not calculate expiration time.")

    return TokenResponse(access_token=token, expires_in=expires_in)


def _load_credentials(credentials_filename: str) -> tuple[str, str]:
    try:
        with open(credentials_filename) as f:
            data = json.load(f)

    except FileNotFoundError:
        raise FileNotFoundError(
            "gcp_credentials.json file not found. Please provide the file."
        )
    except json.JSONDecodeError:
        raise ValueError(
            "Invalid JSON format in gcp_credentials.json. Please check the file."
        )

    try:
        private_key = data["private_key"]
        issuer = data["client_email"]
    except KeyError as e:
        raise KeyError(
            f"Missing key in gcp_credentials.json: {e}. Please check the file."
        )
    return private_key, issuer


class TokenManager:
    def __init__(self, credentials_filename: str = GCP_CREDENTIALS_FILENAME):
        self._lock = asyncio.Lock()
        self._token: str | None = None
        self._expires_at: datetime | None = None
        self._private_key, self._issuer = _load_credentials(credentials_filename)

    def _encode_jwt(self) -> str:
        current_time = int(datetime.now().timestamp())
        return jwt.encode(
            {
                "iss": self._issuer,
                "scope": SCOPE,
                "aud": TOKEN_URL,
                "iat": current_time,
                "exp": current_time + ACCESS_TOKEN_DURATION,
            },
            key=self._private_key,
            algorithm=JWT_ENCRYPTION_ALGORITHM,
            headers={
                "alg": JWT_ENCRYPTION_ALGORITHM,
                "typ": "JWT",
            },
        )

    async def _refresh_token(self) -> None:
        encoded_jwt = self._encode_jwt()
        token_response = await _async_get_token(encoded_jwt)

        async with self._lock:
            self._token = token_response.access_token
            self._expires_at = datetime.now() + timedelta(
                seconds=token_response.expires_in
            )

    def _should_refresh_token(self) -> bool:
        return (
            self._token is None
            or self._expires_at is None
            or datetime.now() >= self._expires_at
        )

    async def get_token(self) -> str:
        if self._should_refresh_token():
            await self._refresh_token()

        if self._token is None:
            raise ValueError("Failed to obtain access token.")

        return self._token
