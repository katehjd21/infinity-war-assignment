import pytest
from werkzeug.exceptions import HTTPException
from helpers.ksb import KsbHelper


# TEST VALIDATE KSB CODE
@pytest.mark.parametrize("valid_code", ["K1", "K1a", "S2", "B3b", "k4", "s5C"])
def test_validate_ksb_code_valid(valid_code):
    assert KsbHelper.validate_ksb_code(valid_code) == valid_code.strip().upper()

@pytest.mark.parametrize("invalid_code", ["", "123", "X1", "A1", "K", "S@", "B#"])
def test_validate_ksb_code_invalid_raises_abort(invalid_code):
    with pytest.raises(HTTPException) as e:
        KsbHelper.validate_ksb_code(invalid_code)
    assert "Invalid KSB Code format" in str(e.value)


# TEST LIST ALL KSBS
def test_list_all_ksbs_returns_all_ksbs(ksbs):
    all_ksbs = KsbHelper.list_all_ksbs()
    types = [knowledge["type"] for knowledge in all_ksbs]
    codes = [knowledge["code"] for knowledge in all_ksbs]

    assert "Knowledge" in types
    assert "Skill" in types
    assert "Behaviour" in types

    for ksb in ksbs:
        assert ksb.code in codes


# TEST GET KSB BY CODE
def test_get_ksb_by_code_returns_serialized_with_duties(duty_with_ksb):
    duty, knowledge, skill, behaviour = duty_with_ksb

    # Knowledge
    serialized = KsbHelper.get_ksb_by_code(knowledge.code)
    assert serialized["code"] == knowledge.code
    assert serialized["type"] == "Knowledge"
    assert serialized["duties"][0]["code"] == duty.code

    # Skill
    serialized = KsbHelper.get_ksb_by_code(skill.code)
    assert serialized["code"] == skill.code
    assert serialized["type"] == "Skill"
    assert serialized["duties"][0]["code"] == duty.code

    # Behaviour
    serialized = KsbHelper.get_ksb_by_code(behaviour.code)
    assert serialized["code"] == behaviour.code
    assert serialized["type"] == "Behaviour"
    assert serialized["duties"][0]["code"] == duty.code


def test_get_ksb_by_code_invalid_format_raises_abort():
    with pytest.raises(HTTPException) as e:
        KsbHelper.get_ksb_by_code("invalid!")
    assert "Invalid KSB Code format" in str(e.value)


def test_get_ksb_by_code_not_found_raises_abort():
    with pytest.raises(HTTPException) as e:
        KsbHelper.get_ksb_by_code("K999")
    assert "KSB not found" in str(e.value)