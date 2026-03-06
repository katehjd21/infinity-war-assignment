from models.duty import Duty

class DutyController:

    @staticmethod
    def fetch_duty(duty_code):
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