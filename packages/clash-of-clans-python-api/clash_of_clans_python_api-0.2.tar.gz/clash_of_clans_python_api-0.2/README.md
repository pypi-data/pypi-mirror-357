# Clash of Clans Python API Wrapper

An (in development) **asynchronous Python wrapper** for the official Clash of Clans API.  
This library simplifies accessing player and clan data, handling authentication, HTTP requests, and response parsing.

## Installation

```bash
pip install -i https://test.pypi.org/simple/ clash-of-clans-api
````

## Usage Example
```python
import asyncio
import os
from coc_api import ClashOfClansAPI
from coc_api.models import Player

API_TOKEN = os.getenv("API_TOKEN")
PLAYER_TAG = "#L8PRCJVL2"

async def main() -> None:
    """
    Example usage of the ClashOfClansAPI to fetch and print player data.
    """
    if not API_TOKEN:
        raise ValueError("API_TOKEN environment variable is not set.")

    api = ClashOfClansAPI(token=API_TOKEN, proxy=True)

    try:
        # Fetch player data
        player: Player = await api.players.get(PLAYER_TAG)
        print("Player Info:")
        print(f"Name: {player.name}")
        print(f"Town Hall Level: {player.town_hall_level}")
        print(f"Clan: {player.clan.name if player.clan else 'No clan'}")
    except Exception as e:
        print("An error occurred while fetching player data:")
        print(repr(e))
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Overview

### `ClashOfClansAPI(token: str, timeout: int = 10, proxy: bool = False)`

Main client class to interact with the Clash of Clans API.

* `token`: Your Clash of Clans API token.
* `timeout`: Request timeout in seconds (default: 10).
* `proxy`: If `True`, routes requests through RoyaleAPI's proxy.

#### Attributes:

* `players`: Access player-related API endpoints.
* `clans`: Access clan-related API endpoints.

### PlayerEndpoints

* `get(player_tag: str) -> Player`

  Fetch detailed information about a player.

* `verify_token(player_tag: str, token: str)`

  Verify a player token with the API.

### ClanEndpoints

* `get(clan_tag: str) -> Clan`

  Fetch detailed information about a clan.