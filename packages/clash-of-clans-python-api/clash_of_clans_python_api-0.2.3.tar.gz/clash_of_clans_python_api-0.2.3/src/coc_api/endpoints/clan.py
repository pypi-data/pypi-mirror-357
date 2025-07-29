from __future__ import annotations
from typing import TYPE_CHECKING
from urllib.parse import quote
from coc_api.models import Clan

if TYPE_CHECKING:
    from coc_api import ClashOfClansAPI

class ClanEndpoints:
    """
    Provides access to clan-related endpoints of the Clash of Clans API.

    Args:
        api (ClashOfClansAPI): Instance of the main API client.
    """
    def __init__(self, api: ClashOfClansAPI):
        self.api = api

    async def get(self, clan_tag: str) -> Clan:
        """
        Retrieve clan data by clan tag.

        Args:
            clan_tag (str): The clan's unique tag (e.g., "#CLAN123").

        Returns:
            Clan: A Clan model instance with the retrieved clan data.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            Exception: For unexpected errors during the request.
        """
        encoded_tag = quote(clan_tag)
        data = await self.api._get(f"/clans/{encoded_tag}")
        return Clan.from_dict(data)
