"""
This script generates an access token to use in the Google Sheets API.
For more details, see: https://developers.google.com/identity/protocols/oauth2/service-account#httprest
"""

import asyncio
from dataclasses import dataclass
import logging
import jwt
from datetime import datetime, timedelta, timezone
import aiohttp
import json

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ACCESS_TOKEN_DURATION = 60 * 60  # 1 hour
JWT_ENCRYPTION_ALGORITHM = "RS256"
GCP_CREDENTIALS_FILENAME = "gcp_credentials.json"

logger = logging.getLogger(__name__)


@dataclass
class TokenResponse:
    """Data class to hold the token response.

    Attributes:
        access_token: The access token string.
        expires_in: The expiration time of the token in seconds.
    """

    access_token: str
    expires_in: int


async def _async_get_token(encoded_jwt: str) -> TokenResponse:
    """Get the access token using the JWT.
    Args:
        encoded_jwt: The encoded JWT.

    Returns:
        TokenResponse: The token response containing the access token and expiration time.

    Raises:
        aiohttp.ClientError: If there is an error with the HTTP request.
        KeyError: If the response does not contain the expected keys.
        ValueError: If the response cannot be parsed as JSON.
    """
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
    except KeyError as e:
        logger.error("Missing key in token response: %s", e)
        raise KeyError("Invalid token response. Please check your credentials.")
    except ValueError:
        logger.error("Invalid token response: %s", token_response)
        raise ValueError("Invalid token response. Could not calculate expiration time.")

    return TokenResponse(access_token=token, expires_in=expires_in)


def _load_credentials(credentials_filename: str) -> tuple[str, str]:
    """Load the GCP credentials from a JSON file.

    Args:
        credentials_filename: The path to the GCP credentials JSON file.

    Returns:
        private_key: The private key from the credentials file.
        issuer: The client email from the credentials file.

    Raises:
        FileNotFoundError: If the credentials file is not found.
        json.JSONDecodeError: If the JSON file is invalid.
        KeyError: If the required keys are missing in the JSON file.
    """
    try:
        with open(credentials_filename) as f:
            data = json.load(f)

    except FileNotFoundError:
        logger.error("gcp_credentials.json file not found.")
        raise FileNotFoundError(
            "gcp_credentials.json file not found. Please provide the file."
        )
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in gcp_credentials.json")
        raise ValueError(
            "Invalid JSON format in gcp_credentials.json. Please check the file."
        )

    try:
        private_key = data["private_key"]
        issuer = data["client_email"]
    except KeyError as e:
        logger.error("Missing key in gcp_credentials.json: %s", e)
        raise KeyError(
            f"Missing key in gcp_credentials.json: {e}. Please check the file."
        )
    return private_key, issuer


class TokenManager:
    """Token manager for handling GCP access tokens.
    This class is responsible for generating and refreshing the access token
    used to authenticate with the Google Sheets API.

    Attributes:
        _lock: An asyncio lock to ensure thread safety when refreshing the token.
        _token: The current access token.
        _expires_at: The expiration time of the current token.
        _private_key: The private key used to sign the JWT.
        _issuer: The client email used as the issuer in the JWT.
    """

    def __init__(self, credentials_filename: str = GCP_CREDENTIALS_FILENAME):
        """Initialize the TokenManager with the credentials file.

        Args:
            credentials_filename: The path to the GCP credentials JSON file.

        Raises:
            FileNotFoundError: If the credentials file is not found.
            json.JSONDecodeError: If the JSON file is invalid.
            KeyError: If the required keys are missing in the JSON file.
        """
        self._lock = asyncio.Lock()
        self._token: str | None = None
        self._expires_at: datetime | None = None
        self._private_key, self._issuer = _load_credentials(credentials_filename)

    def _encode_jwt(self) -> str:
        """Encode the JWT with the required claims.

        Returns:
            encoded_jwt: The encoded JWT as a string.
        """
        current_time = int(datetime.now(timezone.utc).timestamp())
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
        """Refresh the access token by generating a new JWT and making a request to the token endpoint.
        This method is called when the token is expired or not available.
        It uses an asyncio lock to ensure thread safety when refreshing the token.

        Raises:
            aiohttp.ClientError: If there is an error with the HTTP request.
            KeyError: If the response does not contain the expected keys.
            ValueError: If the response cannot be parsed as JSON.
        """
        encoded_jwt = self._encode_jwt()
        token_response = await _async_get_token(encoded_jwt)

        async with self._lock:
            self._token = token_response.access_token
            self._expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=token_response.expires_in
            )

    def _should_refresh_token(self) -> bool:
        """Check if the token should be refreshed.
        This method checks if the token is None or if it has expired.

        Returns:
            should_refresh: True if the token should be refreshed, False otherwise.
        """
        return (
            self._token is None
            or self._expires_at is None
            or datetime.now(timezone.utc) >= self._expires_at
        )

    async def get_token(self) -> str:
        """Get the access token.
        This method checks if the token is expired or not available,
        and refreshes it if necessary.

        Returns:
            token: The access token as a string.

        Raises:
            ValueError: If the token is None after refresh or if there is an error refreshing the token.
        """
        if self._should_refresh_token():
            logger.debug("Token expired or not available. Refreshing token.")
            try:
                await self._refresh_token()
                logger.debug("Token refreshed successfully.")
            except Exception as e:
                logger.error("Error refreshing token: %s", e)
                raise ValueError("Failed to refresh access token.")

        if self._token is None:
            logger.error("Token is None after refresh.")
            raise ValueError("Failed to obtain access token.")

        return self._token
