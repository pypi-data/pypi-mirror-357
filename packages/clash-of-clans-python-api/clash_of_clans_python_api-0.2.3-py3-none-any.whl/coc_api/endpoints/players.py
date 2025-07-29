from __future__ import annotations
from typing import TYPE_CHECKING
from urllib.parse import quote
from coc_api.models import Player

if TYPE_CHECKING:
    from coc_api import ClashOfClansAPI

class PlayerEndpoints:
    """
    Provides access to player-related endpoints of the Clash of Clans API.

    Args:
        api (ClashOfClansAPI): Instance of the main API client.
    """
    def __init__(self, api: 'ClashOfClansAPI'):
        self.api = api

    async def get(self, player_tag: str) -> Player:
        """
        Retrieve player data by player tag.

        Args:
            player_tag (str): The player's unique tag (e.g., "#ABC123").

        Returns:
            Player: A Player model instance with the retrieved player data.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            Exception: For unexpected errors during the request.
        """
        encoded_tag = quote(player_tag)
        data = await self.api._get(f"/players/{encoded_tag}")
        return Player.from_dict(data) 
    
    async def verify_token(self, player_tag: str, token: str) -> dict:
        """
        Verify a player token with the API.

        Args:
            player_tag (str): The player's unique tag.
            token (str): The token string to verify.

        Returns:
            dict: API response confirming verification status.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            Exception: For unexpected errors during the request.
        """
        encoded_tag = quote(player_tag)
        data = {"token": token}
        return await self.api._post(f"/players/{encoded_tag}/verifytoken", json_data=data)
