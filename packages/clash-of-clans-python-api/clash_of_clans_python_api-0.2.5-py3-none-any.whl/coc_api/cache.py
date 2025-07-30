from datetime import datetime, timezone
from typing import Optional
from coc_api.models import Player, Clan
    
class Cache:
    def __init__(self, cache_timeout_minutes: int = 30):
        self.players: dict = {}
        self.clans: dict = {}
        self.cache_timeout: int = cache_timeout_minutes * 60
        self.caching: bool = True if self.cache_timeout > 0 else False
        
    def _key(self, tag: str) -> str:
        return tag.strip().upper()
    
    def _timestamp(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())
        
    def get_player(self, player_tag) -> Optional["Player"]:
        key = self._key(player_tag)
        cache_entry = self.players.get(key)
        if cache_entry:
            old_timestamp = cache_entry["timestamp"]
            current_timestamp = self._timestamp()
            if current_timestamp - old_timestamp <= self.cache_timeout:
                return cache_entry["data"]
            else:
                self.players.pop(key, None)
                return None
        return None
        
    def add_player(self, player: Player) -> None:
        key = self._key(player.tag)
        self.players[key] = {
            "data": player,
            "timestamp": self._timestamp()
        }
    
    def get_clan(self, clan_tag) -> Optional["Clan"]:
        key = self._key(clan_tag)
        cache_entry = self.clans.get(key)
        if cache_entry:
            old_timestamp = cache_entry["timestamp"]
            current_timestamp = self._timestamp()
            if current_timestamp - old_timestamp <= self.cache_timeout:
                return cache_entry["data"]
            else:
                self.clans.pop(key, None)
                return None
        return None
        
    def add_clan(self, clan: Clan) -> None:
        key = self._key(clan.tag)
        self.clans[key] = {
            "data": clan,
            "timestamp": self._timestamp()
        }