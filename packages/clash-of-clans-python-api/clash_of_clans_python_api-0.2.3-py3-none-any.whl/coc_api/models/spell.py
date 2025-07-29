from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Spell:
    name: Optional[str]
    level: Optional[int]
    max_level: Optional[int]
    village: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Spell':
        return cls(
            name=data.get("name"),
            level=data.get("level"),
            max_level=data.get("maxLevel"),
            village=data.get("village")
        )
