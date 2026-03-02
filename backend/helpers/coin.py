import uuid
from flask import abort
from models import Coin, Duty, DutyCoin

class CoinHelper:

    @staticmethod
    def validate_coin_name(name: str, check_exists=True):
        name = name.strip()
        if not name:
            abort(400, description="Coin name cannot be empty.")
        if check_exists and Coin.select().where(Coin.name == name).exists():
            abort(400, description="Coin already exists. Please choose another name.")
        return name


    @staticmethod
    def attach_duties(coin, duty_codes):
        if not isinstance(duty_codes, list):
            abort(400, description="'duty_codes' must be a list of duty codes.")

        for code in duty_codes:
            try:
                duty = Duty.get(Duty.code == code.upper())
                DutyCoin.create(duty=duty, coin=coin)
            except Duty.DoesNotExist:
                abort(400, description=f"Duty with code '{code}' does not exist.")
    
    
    @staticmethod
    def get_coin_by_id(coin_id: str):
        try:
            uuid_obj = uuid.UUID(coin_id)
        except ValueError:
            abort(400, description="Invalid Coin ID format. Coin ID must be a UUID (non-integer).")

        try:
            coin = Coin.get_by_id(uuid_obj)
        except Coin.DoesNotExist:
            abort(404, description="Coin not found.")

        return coin 


    @classmethod
    def create_coin(cls, data: dict, with_duties=True):
        if not data or "name" not in data:
            abort(400, description="Missing 'name' key in request body.")

        name = cls.validate_coin_name(data["name"])

        completed = data.get("completed", False)
        if not isinstance(completed, bool):
            abort(400, description="'completed' must be a boolean.")

        coin = Coin.create(name=name, completed=completed)

        if with_duties:
            duty_codes = data.get("duty_codes", [])
            cls.attach_duties(coin, duty_codes)

        return coin
    

    @classmethod
    def toggle_complete_coin(cls, coin_id: str):
        coin = cls.get_coin_by_id(coin_id)
        coin.completed = not coin.completed
        coin.save()
        return coin.completed


    @classmethod
    def update_coin(cls, coin_id: str, data: dict, require_name=False):
        try:
            uuid_obj = uuid.UUID(coin_id)
        except ValueError:
            abort(400, description="Invalid Coin ID format. Coin ID must be a UUID (non-integer).")

        try:
            coin = Coin.get_by_id(uuid_obj)
        except Coin.DoesNotExist:
            abort(404, description="Coin not found.")

        if require_name:
            if "name" not in data:
                abort(400, description="Missing 'name' key in request body.")
        else:
            if not data:
                abort(400, description="Request body is empty.")

        if "name" in data:
            coin.name = cls.validate_coin_name(data["name"], check_exists=False)

        if "duty_codes" in data:
            DutyCoin.delete().where(DutyCoin.coin == coin).execute()
            cls.attach_duties(coin, data["duty_codes"])

        if "completed" in data:
            if not isinstance(data["completed"], bool):
                abort(400, description="'completed' must be a boolean.")
            coin.completed = data["completed"]

        coin.save()
        return coin


    @staticmethod
    def delete_coin(coin_id: str):
        try:
            uuid_obj = uuid.UUID(coin_id)
        except ValueError:
            abort(400, description="Invalid Coin ID format. Coin ID must be a UUID (non-integer).")

        try:
            coin = Coin.get_by_id(uuid_obj)
        except Coin.DoesNotExist:
            abort(404, description="Coin not found.")

        coin.delete_instance()