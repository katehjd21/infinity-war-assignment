import requests
from api_session import api_session

class Duty:
    def __init__(self, code, name, description, id=None, coins=None, ksbs=None):
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.coins = coins or []
        self.ksbs = ksbs or []
    

    @classmethod
    def fetch_duties_from_backend(cls):
        try:
            response = api_session.get("http://localhost:5000/v2/duties")
            response.raise_for_status()
            duty_data = response.json()
            return [
                cls(
                    code=duty.get("code"),
                    name=duty.get("name", ""),
                    description=duty.get("description", ""),
                    id=duty.get("id"),
                    coins=duty.get("coins", []),
                    ksbs=duty.get("ksbs", [])
                )
                for duty in duty_data
            ]
        except requests.RequestException as e:
            print("Error fetching duties:", e)
            return []
        

    @classmethod
    def fetch_duty_from_backend(cls, code):
        try:
            response = api_session.get(f"http://localhost:5000/duties/{code}")
            response.raise_for_status()
            data = response.json()
            return cls(
                code=data.get("code"),
                name=data.get("name", ""),
                description=data.get("description", ""),
                id=data.get("id"),
                coins=data.get("coins", []),
                ksbs=data.get("ksbs", [])
            )
        except requests.RequestException as e:
            print(f"Error fetching duty {code}:", e)
            return None

    @classmethod
    def create_duty(cls, code, name, description, coin_ids=None, ksb_codes=None):
        try:
            response = api_session.post(
                "http://localhost:5000/v2/duties",
                json={
                    "code": code,
                    "name": name,
                    "description": description,
                    "coin_ids": coin_ids or [],
                    "ksb_codes": ksb_codes or []
                }
            )
            response.raise_for_status()
            data = response.json()
            duty = cls(
                code=data.get("code"),
                name=data.get("name", ""),
                description=data.get("description", ""),
                id=data.get("id"),
                coins=data.get("coins", []),
                ksbs=data.get("ksbs", [])
            )
            return duty, None
        
        
        except requests.HTTPError:
            try:
                error = response.json().get("description") or response.json().get("message")
            except Exception:
                error = "Failed to create duty"

            return None, error

        except requests.RequestException:
            return None, "Server error while creating duty"

    @classmethod
    def update_duty(cls, code, name=None, description=None, coin_ids=None, ksb_codes=None):
        try:
            request_body = {}
            if name is not None:
                request_body["name"] = name
            if description is not None:
                request_body["description"] = description
            if coin_ids is not None:
                request_body["coin_ids"] = coin_ids
            if ksb_codes is not None:
                request_body["ksb_codes"] = ksb_codes

            response = api_session.patch(
                f"http://localhost:5000/v2/duties/{code}",
                json=request_body
            )
            response.raise_for_status()
            data = response.json()
            duty = cls(
                code=data.get("code"),
                name=data.get("name", ""),
                description=data.get("description", ""),
                id=data.get("id"),
                coins=data.get("coins", []),
                ksbs=data.get("ksbs", [])
            )
            return duty, None
        
        except requests.HTTPError:
            try:
                error = response.json().get("description") or response.json().get("message")
            except Exception:
                error = "Failed to update duty"

            return None, error

        except requests.RequestException:
            return None, "Server error while updating duty"

    @classmethod
    def delete_duty(cls, code):
        try:
            response = api_session.delete(f"http://localhost:5000/v2/duties/{code}")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print("Error deleting duty:", e)
            return False