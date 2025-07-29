from dataclasses import dataclass

@dataclass
class Achievement:
    name: str
    stars: int
    value: int
    target: int
    info: str
    completion_info: str
    village: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Achievement':
        return cls(
            name=data.get("name"),
            stars=data.get("stars"),
            value=data.get("value"),
            target=data.get("target"),
            info=data.get("info"),
            completion_info=data.get("completionInfo"),
            village=data.get("village")
        )
