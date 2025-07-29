from functools import wraps
from typing import Callable, Awaitable, Optional, Type, TypeVar, Union
from typing import Optional
from coc_api.models import Player, Clan

F = TypeVar('F', bound=Callable[..., Awaitable[Union["Player", "Clan"]]])

def cache_result(data_cls: Type[Union["Player", "Clan"]]):
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(self, tag: str) -> Optional[Union["Player", "Clan"]]:
            if data_cls is Player:
                cached = self.cache.get_player(tag)
            elif data_cls is Clan:
                cached = self.cache.get_clan(tag)
            else:
                cached = None

            if cached:
                return cached

            result = await func(self, tag)

            if result is not None:
                if data_cls is Player:
                    self.cache.add_player(result)
                elif data_cls is Clan:
                    self.cache.add_clan(result)

            return result
        return wrapper
    return decorator