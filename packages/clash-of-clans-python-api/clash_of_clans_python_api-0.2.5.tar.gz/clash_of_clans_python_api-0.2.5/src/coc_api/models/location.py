from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Location:
    id: Optional[int]
    name: Optional[str]
    is_country: Optional[bool]
    country_code: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            is_country=data.get("isCountry"),
            country_code=data.get("countryCode")
        )
