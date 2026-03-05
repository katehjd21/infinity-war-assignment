import requests
from api_session import api_session


class Duty:
    def __init__(self, code, name, description, coins=None):
        self.code = code
        self.name = name
        self.description = description
        self.coins = coins or [] 

    @classmethod
    def fetch_duty_from_backend(cls, duty_code):
        try:
            response = api_session.get(f"http://localhost:5000/duties/{duty_code}")
            response.raise_for_status()
            data = response.json()
            return cls(
                code=data["code"],
                name=data.get("name", ""),
                description=data.get("description", ""),
                coins=data.get("coins", [])
            )
        except requests.RequestException as e:
            print(f"Error fetching duty {duty_code}:", e)
            return None