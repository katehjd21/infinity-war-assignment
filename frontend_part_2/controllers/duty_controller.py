from models.duty import Duty

class DutyController:
    @staticmethod
    def fetch_duty(duty_code):
        try:
            return Duty.fetch_duty_from_backend(duty_code)
        except Exception as e:
            print(f"Error fetching duty {duty_code}: {e}")
            return None