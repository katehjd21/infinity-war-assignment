import uuid
from flask import abort
from peewee import IntegrityError
from pg_db_connection import database
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
    def validate_coin_id(coin_id: str):
        try:
            uuid_obj = uuid.UUID(coin_id)
        except ValueError:
            abort(400, description=f"Invalid Coin ID: {coin_id}. Coin ID must be a UUID (non-integer).")

        coin = Coin.get_or_none(id=str(uuid_obj))  
        if coin is None:
            abort(404, description="Coin not found.")

        return coin


    @staticmethod
    def attach_duties(coin, duty_codes):
        if not isinstance(duty_codes, list):
            abort(400, description="'duty_codes' must be a list")

        invalid_codes = []
        valid_duties = []

        for code in duty_codes:
            duty = Duty.get_or_none(Duty.code == code.upper())
            if duty:
                valid_duties.append(duty)
            else:
                invalid_codes.append(code)

        if invalid_codes:
            abort(400, description=f"Invalid duty codes: {', '.join(invalid_codes)}")

        for duty in valid_duties:
            DutyCoin.get_or_create(duty=duty, coin=coin)


    @classmethod
    def create_coin(cls, data: dict, with_duties=True):
        if not data or "name" not in data:
            abort(400, description="Missing 'name' key in request body.")

        name = cls.validate_coin_name(data["name"])
        completed = data.get("completed", False)
        if not isinstance(completed, bool):
            abort(400, description="'completed' must be a boolean.")

        duty_codes = data.get("duty_codes", []) if with_duties else []

        try:
            with database.atomic():
                coin = Coin.create(name=name, completed=completed)
                if with_duties and duty_codes:
                    cls.attach_duties(coin, duty_codes)
                return coin
        except IntegrityError as e:
            abort(400, description=f"Coin creation failed: {e}")


    @classmethod
    def update_coin(cls, coin_id: str, data: dict, require_name=False):
        coin = cls.validate_coin_id(coin_id)

        if require_name and "name" not in data:
            abort(400, description="Missing 'name' key in request body.")
        if not data:
            abort(400, description="Request body is empty.")

        try:
            with database.atomic():
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
        except IntegrityError as e:
            abort(400, description=f"Coin update failed: {e}")


    @classmethod
    def toggle_complete_coin(cls, coin_id: str):
        coin = cls.validate_coin_id(coin_id)
        coin.completed = not coin.completed
        coin.save()
        return coin.completed


    @staticmethod
    def get_coin_by_id(coin_id: str):
        return CoinHelper.validate_coin_id(coin_id)


    @staticmethod
    def delete_coin(coin_id: str):
        coin = CoinHelper.validate_coin_id(coin_id)
        coin.delete_instance()