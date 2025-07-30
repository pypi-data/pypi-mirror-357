from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone

@dataclass
class GoldPass:
    start_time: Optional[Union[datetime, int]]
    end_time: Optional[Union[datetime, int]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoldPass':
        start_time, end_time = data.get("startTime"), data.get("endTime")
        if start_time and end_time:
            dt_start_time = datetime.strptime(start_time, "%Y%m%dT%H%M%S.%fZ")
            dt_start_time = dt_start_time.replace(tzinfo=timezone.utc)
            dt_end_time = datetime.strptime(end_time, "%Y%m%dT%H%M%S.%fZ")
            dt_end_time = dt_end_time.replace(tzinfo=timezone.utc)
        return cls(
            start_time=dt_start_time,
            end_time=dt_end_time
        )