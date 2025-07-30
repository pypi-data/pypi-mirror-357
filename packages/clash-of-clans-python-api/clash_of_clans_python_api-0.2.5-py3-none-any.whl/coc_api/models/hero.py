from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from coc_api.models import Equipment

@dataclass
class Hero:
    name: Optional[str]
    level: Optional[int]
    max_level: Optional[int]
    village: Optional[str]
    equipment: List[Equipment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hero':
        equipment_data = data.get("equipment", [])
        equipment = [Equipment.from_dict(e) for e in equipment_data]
        return cls(
            name=data.get("name"),
            level=data.get("level"),
            max_level=data.get("maxLevel"),
            village=data.get("village"),
            equipment=equipment
        )