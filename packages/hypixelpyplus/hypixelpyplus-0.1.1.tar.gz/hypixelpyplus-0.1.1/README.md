hypixelpyplus is a lightweight Python wrapper for the Hypixel API, allowing you to fetch player stats, guild information, status, recent games, and more.

## Installation

```bash
pip install hypixelpyplus
````

## Usage

```python
import hypixelpyplus

client = hypixelpyplus.HypixelClient("your-api-key")

player = client.get_player("Notch")
print(player["player"]["rank"])
```

## Features

* Get player stats by username or UUID
* Fetch guild info by player UUID or guild name
* Retrieve friends, status, and recent games
* Get API key info and Mojang UUID lookup

## Methods

* get_key_info()
* get_player(uuid_or_name: str)
* get_guild_by_player(uuid: str)
* get_guild_by_name(name: str)
* get_friends(uuid: str)
* get_status(uuid: str)
* get_recent_games(uuid: str)
* get_uuid(username: str)

## License

MIT