from models.duty import Duty

class DutyController:

    @staticmethod
    def fetch_duty(duty_code):
        return Duty.fetch_duty_from_backend(duty_code)