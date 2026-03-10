import requests
from api_session import api_session
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

class Coin:
    def __init__(self, name, id=None, duties=None, completed=False):
        self.name = name
        self.id = id
        self.duties = duties or [] 
        self.completed = completed

    @classmethod
    def fetch_coins_from_backend(cls):
        try:
            response = api_session.get(f"{BACKEND_URL}/v3/coins")
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
            response = api_session.get(f"{BACKEND_URL}/v3/coins/{coin_id}")
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
            response = api_session.post(f"{BACKEND_URL}/coins/{coin_id}/complete")
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
    def create_coin(cls, name, duty_codes=None, completed=False):
        try:
            response = api_session.post(
                f"{BACKEND_URL}/v3/coins",
                json={
                    "name": name,
                    "duty_codes": duty_codes or [],
                    "completed": completed
                }
            )

            response.raise_for_status()
            data = response.json()

            coin = cls(
                data["name"],
                data["id"],
                data.get("duties", []),
                data.get("completed", False)
            )

            return coin, None

        except requests.HTTPError:
            try:
                error = response.json().get("description") or response.json().get("message")
            except Exception:
                error = "Failed to create coin"

            return None, error

        except requests.RequestException:
            return None, "Server error while creating coin"
            
    
    @classmethod
    def update_coin(cls, coin_id, name=None, duty_codes=None, completed=False):
        try:
            request_body = {}

            if name is not None:
                request_body["name"] = name

            if duty_codes is not None:
                request_body["duty_codes"] = duty_codes
            
            if completed is not None:
                request_body["completed"] = completed

            response = api_session.patch(
                f"{BACKEND_URL}/v3/coins/{coin_id}",
                json=request_body
            )

            response.raise_for_status()
            data = response.json()

            coin = cls(
                data["name"],
                data["id"],
                data.get("duties", []),
                data.get("completed", False)
            )

            return coin, None

        except requests.HTTPError:
            try:
                error = response.json().get("description") or response.json().get("message")
            except Exception:
                error = "Failed to update coin"

            return None, error

        except requests.RequestException:
            return None, "Server error while updating coin"
        

    @classmethod
    def delete_coin(cls, coin_id):
        try:
            response = api_session.delete(
                f"{BACKEND_URL}/v2/coins/{coin_id}"
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print("Error deleting coin:", e)
            return False