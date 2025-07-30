from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ClanCapitalHouse:
    type: Optional[str]
    id: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClanCapitalHouse':
        return cls(
            type=data.get("type"),
            id=data.get("id")
        )