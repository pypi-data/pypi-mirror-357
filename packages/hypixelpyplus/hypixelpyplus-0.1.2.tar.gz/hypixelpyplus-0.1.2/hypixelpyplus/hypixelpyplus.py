import requests

class Error(Exception):
    pass

class APIError(Exception):
    pass

class HypixelClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hypixel.net"

    def _request(self, endpoint: str, params: dict = None):
        if params is None:
            params = {}
        params['key'] = self.api_key
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        data = response.json()
        if not data.get("success", False):
            raise APIError(data.get("cause", "Unknown error"))
        return data

    def get_player(self, uuid_or_name: str):
        if "-" in uuid_or_name or len(uuid_or_name) == 32:
            return self._request("v2/player", {"uuid": uuid_or_name})
        uuid = self.get_uuid(uuid_or_name)
        return self._request("v2/player", {"uuid": uuid})

    def get_guild_by_player(self, uuid: str):
        return self._request("v2/guild", {"player": uuid})

    def get_guild_by_name(self, name: str):
        return self._request("v2/guild", {"name": name})

    def get_friends(self, uuid: str):
        return self._request("v2/friends", {"uuid": uuid})

    def get_status(self, uuid: str):
        return self._request("v2/status", {"uuid": uuid})

    def get_recent_games(self, uuid: str):
        return self._request("v2/recentgames", {"uuid": uuid})

    def get_uuid(self, username: str):
        r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if r.status_code != 200:
            raise Error("Invalid username")
        return r.json()["id"]