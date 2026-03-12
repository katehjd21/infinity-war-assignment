from models.duty import Duty
from models.coin import Coin
from utils.helpers import load_fixture

class DutyController:

    @staticmethod
    def fetch_all_duties(testing=False):
        if testing:
            duties_data = load_fixture("duties.json")
            duties = []
            for d in duties_data:
                d["coins"] = [Coin(c["name"], c["id"]) for c in d.get("coins", [])]
                duties.append(d)
            return duties
        return Duty.fetch_duties_from_backend()

    @staticmethod
    def fetch_duty(duty_code, testing=False):
        if testing:
            duties_data = load_fixture("duties.json")
            duty_dict = next((d for d in duties_data if d["code"] == duty_code), None)
            if duty_dict:
                duty_dict["coins"] = [Coin(c["name"], c["id"]) for c in duty_dict.get("coins", [])]
            return duty_dict
        return Duty.fetch_duty_from_backend(duty_code)

    @staticmethod
    def create_duty(code, name, description, coin_ids=None, ksb_codes=None):
        return Duty.create_duty(code, name, description, coin_ids, ksb_codes)

    @staticmethod
    def update_duty(code, name=None, description=None, coin_ids=None, ksb_codes=None):
        return Duty.update_duty(code, name, description, coin_ids, ksb_codes)

    @staticmethod
    def delete_duty(code):
        return Duty.delete_duty(code)