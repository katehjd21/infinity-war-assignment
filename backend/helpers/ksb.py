from models import Knowledge, Skill, Behaviour
import re
from flask import abort
from utils.helper_functions import serialize_ksb, serialize_ksb_with_duties


class KsbHelper:

    @staticmethod
    def validate_ksb_code(ksb_code):
        ksb_code = ksb_code.strip().upper()
        regex = r"^[KSB]\d+[a-zA-Z]?$"
        if not re.match(regex, ksb_code):
            abort(400, description="Invalid KSB Code format. KSB Code must start with 'K', 'S', or 'B', followed by numbers and optionally a letter (e.g., K1, K1a, S2, B3b).")
        return ksb_code

    @staticmethod
    def list_all_ksbs():
        ksbs_list = []
        for model, ksb_type in [(Knowledge, "Knowledge"), (Skill, "Skill"), (Behaviour, "Behaviour")]:
            ksbs_list.extend([serialize_ksb(k, ksb_type) for k in model.select()])
        return ksbs_list

    @staticmethod
    def get_ksb_by_code(ksb_code):
        ksb_code = KsbHelper.validate_ksb_code(ksb_code)
        for model, ksb_type_name in [(Knowledge,"Knowledge"),(Skill,"Skill"),(Behaviour,"Behaviour")]:
            try:
                ksb = model.get(model.code == ksb_code)
                return serialize_ksb_with_duties(ksb, ksb_type_name)
            except model.DoesNotExist:
                continue
        abort(404, description="KSB not found.")