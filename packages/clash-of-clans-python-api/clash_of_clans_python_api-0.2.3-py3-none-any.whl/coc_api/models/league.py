from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal

@dataclass
class League:
    id: Optional[int]
    name: Optional[str]
    icon: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any], icon_size: Literal["tiny", "small", "medium"] = "small") -> 'League':
        icon = data.get("iconUrls", {}).get(icon_size)
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            icon=icon
        )
