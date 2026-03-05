import requests
from api_session import api_session

class Coin:
    def __init__(self, name, id=None, duties=None, completed=False):
        self.name = name
        self.id = id
        self.duties = duties or [] 
        self.completed = completed

    @classmethod
    def fetch_coins_from_backend(cls):
        try:
            response = api_session.get("http://localhost:5000/v3/coins")
            response.raise_for_status()
            coins_data = response.json()
            return [
                cls(
                    coin["name"],
                    coin["id"],
                    coin.get("duties", []),
                    coin.get("completed", False)
                )
                for coin in coins_data
            ]
        except requests.RequestException as e:
            print("Error fetching coins:", e)
            return []

    @classmethod
    def fetch_coin_from_backend_by_id(cls, coin_id):
        try:
            response = api_session.get(f"http://localhost:5000/v3/coins/{coin_id}")
            response.raise_for_status()
            coin_data = response.json()
            return cls(
                coin_data["name"],
                coin_data["id"],
                coin_data.get("duties", []),
                coin_data.get("completed", False)
            )
        except requests.RequestException as e:
            print(f"Error fetching coin {coin_id}:", e)
            return None