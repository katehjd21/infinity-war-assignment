import requests

class Coin:
    def __init__(self, name, id=None, duties=None):
        self.name = name
        self.id = id
        self.duties = duties or []

    @staticmethod
    def fetch_coins_from_backend():
        try:
            response = requests.get("http://localhost:5000/v2/coins")
            response.raise_for_status()
            coins_data = response.json()
            return [Coin(coin["name"], coin["id"]) for coin in coins_data]
        except requests.RequestException as e:
            print("Error fetching coins:", e)
            return []
    
    @staticmethod
    def fetch_coin_from_backend_by_id(coin_id):
        try:
            response = requests.get(f"http://localhost:5000/v2/coins/{coin_id}")
            response.raise_for_status()
            coin_data = response.json()
            return Coin(
                coin_data["name"],
                coin_data["id"],
                coin_data.get("duties", [])
            )
        except requests.RequestException as e:
            print(f"Error fetching coin {coin_id}:", e)
            return None
    
