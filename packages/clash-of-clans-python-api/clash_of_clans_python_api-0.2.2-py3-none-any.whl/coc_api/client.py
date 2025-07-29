import httpx
from typing import Optional
from httpx import HTTPStatusError

from coc_api.endpoints import PlayerEndpoints
from coc_api.endpoints import ClanEndpoints
from coc_api.exceptions import InvalidTokenError, NotFoundError

BASE_URL = "https://api.clashofclans.com/v1"
PROXY_URL = "https://cocproxy.royaleapi.dev/v1"

class ClashOfClansAPI:
    """
    Asynchronous Python wrapper for the Clash of Clans API.

    Provides easy access to various endpoints such as players and clans,
    handling authentication, requests, and response parsing.

    Args:
        token (str): Clash of Clans API token for authorization.
        timeout (int, optional): Timeout in seconds for API requests. Defaults to 10.
        proxy (bool, optional): Whether to route requests through RoyaleAPI's proxy. Defaults to False.
    """
    def __init__(self, token: str, timeout: int = 10, proxy: bool = False):
        if not token:
            raise InvalidTokenError("API token must be provided and cannot be empty.")

        self.token = token
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=timeout)
        self.proxy = proxy

        # Initialize endpoint interfaces
        self.players = PlayerEndpoints(self)
        self.clans = ClanEndpoints(self)

    async def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Internal helper to perform an asynchronous HTTP GET request.

        Args:
            endpoint (str): API endpoint path (e.g., '/players/{tag}').
            params (Optional[dict]): Query parameters to include in the request.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            httpx.HTTPStatusError: When the response status code indicates an error.
            Exception: For unexpected errors during the request.
        """
        url = f"{PROXY_URL if self.proxy else BASE_URL}{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as http_err:
            if http_err.response.status_code == 404 and http_err.response.json().get("reason") == "notFound":
                raise NotFoundError("Can't find the requested resource.")
            elif http_err.response.status_code == 403 and http_err.response.json().get("reason") == "accessDenied":
                raise InvalidTokenError("Incorrect API token.")
            elif http_err.response.status_code == 403 and http_err.response.json().get("reason") == "accessDenied.invalidIp":
                raise InvalidTokenError(f"{http_err.response.json().get("message").lstrip("Invalid authorization:")}.")
            print(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
            raise
        except Exception as err:
            print(f"Unexpected error: {err}")
            raise

    async def _post(self, endpoint: str, json_data: dict) -> dict:
        """
        Internal helper to perform an asynchronous HTTP POST request.

        Args:
            endpoint (str): API endpoint path.
            json_data (dict): JSON-serializable dictionary to send as the request body.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            httpx.HTTPStatusError: When the response status code indicates an error.
            Exception: For unexpected errors during the request.
        """
        url = f"{BASE_URL}{endpoint}"
        try:
            response = await self.client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as http_err:
            print(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
            raise
        except Exception as err:
            print(f"Unexpected error: {err}")
            raise

    async def close(self) -> None:
        """
        Close the underlying HTTP client session.

        This should be called when the API wrapper is no longer needed
        to properly clean up resources.
        """
        await self.client.aclose()
