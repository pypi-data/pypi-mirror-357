from __future__ import annotations
from typing import TYPE_CHECKING
from coc_api.models import GoldPass

if TYPE_CHECKING:
    from coc_api import ClashOfClansAPI
    
class GoldPassEndpoints:
    def __init__(self, api: 'ClashOfClansAPI'):
        self.api = api
        
    async def get(self, unix: bool = False) -> GoldPass:
        """
        Retreives start and endtime for the current goldpass season.
        
        Args:
            unix (bool): If set to true returns the start_time and end_time as unix time instead of datetime.datetime. Defaults to False.
        """
        data = await self.api._get(f"/goldpass/seasons/current")
        goldpass = GoldPass.from_dict(data)
        if unix:
            goldpass.start_time = int(goldpass.start_time.timestamp())
            goldpass.end_time = int(goldpass.end_time.timestamp())
        return goldpass