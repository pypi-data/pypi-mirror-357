from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from coc_api.models import District

@dataclass
class ClanCapital:
    capital_hall_level: int
    districts: List['District'] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClanCapital":
        from coc_api.models import District
        return cls(
            capital_hall_level=data.get("capitalHallLevel"),
            districts=[District.from_dict(d) for d in data.get("districts", [])]
        )