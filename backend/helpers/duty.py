import re
import uuid
from flask import abort
from models import Duty, Coin, DutyCoin
from utils.helper_functions import serialize_duty, serialize_duty_with_coins_and_ksbs
from models import DutyKnowledge, DutySkill, DutyBehaviour, Knowledge, Skill, Behaviour

class DutyHelper:

    @staticmethod
    def validate_duty_code(duty_code: str, check_exists=True):
        duty_code = duty_code.strip().upper()

        if not duty_code:
            abort(400, description="Duty code cannot be empty.")

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
    def attach_coins_to_duty(duty, coin_ids):
        if not isinstance(coin_ids, list):
            abort(400, description="'coin_ids' must be a list of UUIDs.")

        for coin_id in coin_ids:
            try:
                uuid_obj = uuid.UUID(coin_id)
                coin = Coin.get_by_id(uuid_obj)
                DutyCoin.get_or_create(duty=duty, coin=coin)
            except (ValueError, Coin.DoesNotExist):
                abort(400, description=f"Invalid coin id: {coin_id}")
    

    @staticmethod
    def attach_ksbs_to_duty(duty, ksb_codes: list):
        for code in ksb_codes:
            ksb_type = code[0].upper()
            if ksb_type == "K":
                ksb = Knowledge.get_or_none(Knowledge.code == code.upper())
                if ksb:
                    DutyKnowledge.create(duty=duty, knowledge=ksb)
            elif ksb_type == "S":
                ksb = Skill.get_or_none(Skill.code == code.upper())
                if ksb:
                    DutySkill.create(duty=duty, skill=ksb)
            elif ksb_type == "B":
                ksb = Behaviour.get_or_none(Behaviour.code == code.upper())
                if ksb:
                    DutyBehaviour.create(duty=duty, behaviour=ksb)
    

    @staticmethod
    def list_all_duties():
        duties = Duty.select()
        return [serialize_duty(duty) for duty in duties]

    
    @staticmethod
    def get_duty_by_code(duty_code):
        duty_code = duty_code.strip().upper()
        if not re.match(r"^D\d+$", duty_code):
            abort(
                400,
                description="Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7)."
            )

        try:
            duty = Duty.get(Duty.code == duty_code)
            return serialize_duty_with_coins_and_ksbs(duty)
        except Duty.DoesNotExist:
            abort(404, description="Duty not found.")


    @classmethod
    def create_duty(cls, data: dict):
        if not data:
            abort(400, description="Request body missing.")

        required_fields = ["code", "name", "description"]
        for field in required_fields:
            if field not in data:
                abort(400, description=f"Missing '{field}' key in request body.")

        code = cls.validate_duty_code(data["code"])
        name = cls.validate_duty_name(data["name"])
        description = cls.validate_duty_description(data["description"])

        duty = Duty.create(code=code, name=name, description=description)

        if "coin_ids" in data:
            cls.attach_coins_to_duty(duty, data["coin_ids"])

        if "ksb_codes" in data:
            cls.attach_ksbs_to_duty(duty, data["ksb_codes"])

        return duty


    @classmethod
    def update_duty(cls, duty_code: str, data: dict):
        duty_code = duty_code.upper()

        if not re.match(r"^D\d+$", duty_code):
            abort(400, description="Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7).")

        try:
            duty = Duty.get(Duty.code == duty_code)
        except Duty.DoesNotExist:
            abort(404, description="Duty not found.")

        if "code" in data:
            new_code = cls.validate_duty_code(data["code"], check_exists=False)
            duty.code = new_code

        if "name" in data:
            new_name = cls.validate_duty_name(data["name"], check_exists=False)
            duty.name = new_name

        if "description" in data:
            new_description = cls.validate_duty_description(data["description"])
            duty.description = new_description

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


    @staticmethod
    def delete_duty(duty_code: str):
        duty_code = duty_code.upper()

        if not re.match(r"^D\d+$", duty_code):
            abort(400, description="Invalid Duty Code format. Duty Code must start with a 'D' (case-insensitive) followed by numbers (e.g., D7 or d7).")

        try:
            duty = Duty.get(Duty.code == duty_code)
        except Duty.DoesNotExist:
            abort(404, description="Duty not found.")

        DutyCoin.delete().where(DutyCoin.duty == duty).execute()
        duty.delete_instance()