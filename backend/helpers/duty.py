import re
import uuid
from flask import abort
from peewee import IntegrityError
from werkzeug.exceptions import HTTPException
from pg_db_connection import database
from models import Duty, Coin, DutyCoin
from utils.helper_functions import serialize_duty, serialize_duty_with_coins_and_ksbs
from models import DutyKnowledge, DutySkill, DutyBehaviour, Knowledge, Skill, Behaviour

class DutyHelper:

    @staticmethod
    def validate_duty_code(duty_code: str, check_exists=True):
        if not duty_code:
            abort(400, description="Duty code cannot be empty.")

        duty_code = duty_code.strip().upper()

        if not re.match(r"^D\d+$", duty_code):
            abort(
                400,
                description="Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7).",
            )

        if check_exists and Duty.select().where(Duty.code == duty_code).exists():
            abort(400, description="Duty code already exists.")

        return duty_code


    @staticmethod
    def validate_duty_name(duty_name: str, check_exists=True):
        if not duty_name:
            abort(400, description="Duty name cannot be empty.")
        duty_name = duty_name.strip()
        if not duty_name:
            abort(400, description="Duty name cannot be empty.")
        if check_exists and Duty.select().where(Duty.name == duty_name).exists():
            abort(400, description="Duty name already exists.")
        return duty_name


    @staticmethod
    def validate_duty_description(duty_description: str):
        duty_description = duty_description.strip()
        if not duty_description:
            abort(400, description="Duty description cannot be empty.")
        return duty_description


    @staticmethod
    def validate_coin_id(coin_id: str):
        try:
            uuid_obj = uuid.UUID(coin_id)
            coin = Coin.get_by_id(uuid_obj)
            return coin
        except (ValueError, Coin.DoesNotExist):
            abort(400, description=f"Invalid coin id: {coin_id}")


    @staticmethod
    def attach_coins_to_duty(duty, coin_ids):
        if not isinstance(coin_ids, list):
            abort(400, description="'coin_ids' must be a list")

        invalid_ids = []
        valid_coins = []

        for coin_id in coin_ids:
            try:
                coin = DutyHelper.validate_coin_id(coin_id)
                valid_coins.append(coin)
            except HTTPException:
                invalid_ids.append(coin_id)

        if invalid_ids:
            abort(400, description=f"Invalid coin IDs: {', '.join(invalid_ids)}")

        for coin in valid_coins:
            DutyCoin.get_or_create(duty=duty, coin=coin)


    @staticmethod
    def attach_ksbs_to_duty(duty, ksb_codes: list):
        if not isinstance(ksb_codes, list):
            abort(400, description="'ksb_codes' must be a list")

        invalid_codes = []

        for code in ksb_codes:
            if not code or len(code) < 1:
                invalid_codes.append(code)
                continue

            ksb_type = code[0].upper()
            code_upper = code.upper()

            if ksb_type == "K":
                ksb = Knowledge.get_or_none(Knowledge.code == code_upper)
                if not ksb:
                    invalid_codes.append(code)
                else:
                    DutyKnowledge.get_or_create(duty=duty, knowledge=ksb)

            elif ksb_type == "S":
                ksb = Skill.get_or_none(Skill.code == code_upper)
                if not ksb:
                    invalid_codes.append(code)
                else:
                    DutySkill.get_or_create(duty=duty, skill=ksb)

            elif ksb_type == "B":
                ksb = Behaviour.get_or_none(Behaviour.code == code_upper)
                if not ksb:
                    invalid_codes.append(code)
                else:
                    DutyBehaviour.get_or_create(duty=duty, behaviour=ksb)

            else:
                invalid_codes.append(code)

        if invalid_codes:
            abort(400, description=f"Invalid KSB codes: {', '.join(invalid_codes)}")

    @staticmethod
    def list_all_duties(full: bool = False):
        duties = Duty.select()
        if full:
            return [serialize_duty_with_coins_and_ksbs(d) for d in duties]
        return [serialize_duty(d) for d in duties]

    @classmethod
    def create_duty(cls, data: dict):
        if not data:
            abort(400, description="Request body missing.")

        code = cls.validate_duty_code(data.get("code"))

        name = cls.validate_duty_name(data.get("name"))
        description = cls.validate_duty_description(data.get("description"))

        coin_ids = data.get("coin_ids", [])
        ksb_codes = data.get("ksb_codes", [])

        for coin_id in coin_ids:
            cls.validate_coin_id(coin_id)
        for ksb_code in ksb_codes:
            if not ksb_code or len(ksb_code) < 1:
                abort(400, description=f"Invalid KSB code: {ksb_code}")

        try:
            with database.atomic():
                duty = Duty.create(code=code, name=name, description=description)
                if coin_ids:
                    cls.attach_coins_to_duty(duty, coin_ids)
                if ksb_codes:
                    cls.attach_ksbs_to_duty(duty, ksb_codes)
                return duty
        except IntegrityError as e:
            abort(400, description=f"Duty creation failed: {e}")


    @classmethod
    def update_duty(cls, duty_code: str, data: dict):
        code = DutyHelper.validate_duty_code(duty_code, check_exists=False)
        duty = Duty.get_or_none(Duty.code == code)
        if not duty:
            abort(404, description="Duty not found.")

        try:
            with database.atomic():
                if "code" in data:
                    duty.code = cls.validate_duty_code(data["code"], check_exists=False)
                if "name" in data:
                    duty.name = cls.validate_duty_name(data["name"], check_exists=False)
                if "description" in data:
                    duty.description = cls.validate_duty_description(data["description"])
                duty.save()

                if "coin_ids" in data:
                    DutyCoin.delete().where(DutyCoin.duty == duty).execute()
                    cls.attach_coins_to_duty(duty, data["coin_ids"])
                if "ksb_codes" in data:
                    DutyKnowledge.delete().where(DutyKnowledge.duty == duty).execute()
                    DutySkill.delete().where(DutySkill.duty == duty).execute()
                    DutyBehaviour.delete().where(DutyBehaviour.duty == duty).execute()
                    cls.attach_ksbs_to_duty(duty, data["ksb_codes"])

                return duty
        except IntegrityError as e:
            abort(400, description=f"Duty update failed: {e}")


    @staticmethod
    def get_duty_by_code(duty_code):
        if not duty_code.upper().startswith("D") or not duty_code[1:].isdigit():
            abort(400, description="Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7).")
        
        duty = Duty.get_or_none(Duty.code == duty_code.upper())
        if not duty:
            abort(404, description="Duty not found.")
        return serialize_duty_with_coins_and_ksbs(duty)


    @staticmethod
    def delete_duty(duty_code: str):
        code = DutyHelper.validate_duty_code(duty_code, check_exists=False)
        duty = Duty.get_or_none(Duty.code == code)
        if not duty:
            abort(404, description="Duty not found.")
        DutyCoin.delete().where(DutyCoin.duty == duty).execute()
        duty.delete_instance()