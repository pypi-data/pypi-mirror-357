from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class District:
    id: Optional[int]
    name: Optional[str]
    district_hall_level: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'District':
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            district_hall_level=data.get("DistrictHallLevel")
        )
