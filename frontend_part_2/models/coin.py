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
    
    @classmethod
    def toggle_complete(cls, coin_id):
        try:
            response = api_session.post(f"http://localhost:5000/coins/{coin_id}/complete")
            response.raise_for_status()
            data = response.json()
            if "id" in data:
                return cls(
                    data["name"],
                    data["id"],
                    data.get("duties", []),
                    data.get("completed", False)
                )
            return True
        except requests.RequestException as e:
            print(f"Error toggling coin {coin_id}:", e)
            return None
    
    
    @classmethod
    def create_coin(cls, name, duty_codes=None):
        try:
            response = api_session.post(
                "http://localhost:5000/v3/coins",
                json={
                    "name": name,
                    "duty_codes": duty_codes or []
                }
            )

            response.raise_for_status()
            data = response.json()

            return cls(
                data["name"],
                data["id"],
                data.get("duties", []),
                data.get("completed", False)
            )

        except requests.RequestException as e:
            print("Error creating coin:", e)
            return None
        
    
    @classmethod
    def update_coin(cls, coin_id, name=None, duty_codes=None):
        try:
            request_body = {}

            if name is not None:
                request_body["name"] = name

            if duty_codes is not None:
                request_body["duty_codes"] = duty_codes

            response = api_session.patch(
                f"http://localhost:5000/v3/coins/{coin_id}",
                json=request_body
            )

            response.raise_for_status()
            data = response.json()

            return cls(
                data["name"],
                data["id"],
                data.get("duties", []),
                data.get("completed", False)
            )

        except requests.RequestException as e:
            print("Error updating coin:", e)
            return None
    

    @classmethod
    def delete_coin(cls, coin_id):
        try:
            response = api_session.delete(
                f"http://localhost:5000/v2/coins/{coin_id}"
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print("Error deleting coin:", e)
            return False
