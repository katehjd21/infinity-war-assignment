import pytest
import uuid
from models import DutyCoin, Duty
from helpers.duty import DutyHelper
from werkzeug.exceptions import HTTPException
from models import Duty, Knowledge, Skill, Behaviour, DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour

# VALIDATE DUTY CODE
def test_validate_duty_code_empty(client):
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_code(None)
    assert e.value.code == 400
    assert "cannot be empty" in e.value.description

    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_code("")
    assert e.value.code == 400
    assert "cannot be empty" in e.value.description


def test_validate_duty_code_invalid_format(client):
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_code("X1")
    assert e.value.code == 400
    assert "Invalid Duty Code format" in e.value.description


def test_validate_duty_code_existing(duty_with_coins):
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_code(duty_with_coins.code)
    assert e.value.code == 400
    assert "already exists" in e.value.description


def test_validate_duty_code_valid():
    result = DutyHelper.validate_duty_code(" d99 ")
    assert result == "D99"


# VALIDATE DUTY NAME 
def test_validate_duty_name_empty():
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_name("")
    assert e.value.code == 400


def test_validate_duty_name_existing(duty_with_coins):
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_name(duty_with_coins.name)
    assert e.value.code == 400


def test_validate_duty_name_valid():
    name = "  New Duty  "
    result = DutyHelper.validate_duty_name(name)
    assert result == "New Duty"


# VALIDATE DUTY DESCRIPTION
def test_validate_duty_description_empty():
    with pytest.raises(HTTPException) as e:
        DutyHelper.validate_duty_description("")
    assert e.value.code == 400


def test_validate_duty_description_valid():
    description = "  Duty Description  "
    result = DutyHelper.validate_duty_description(description)
    assert result == "Duty Description"


# ATTACH COINS
def test_attach_coins_creates_associations(duties, coins):
    duty = duties[0]
    coin_ids = [str(coin.id) for coin in coins[:2]]
    
    DutyHelper.attach_coins_to_duty(duty, coin_ids)

    associated_coins = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == duty)]
    assert set(associated_coins) == set([coin.id for coin in coins[:2]])


def test_attach_coins_invalid_uuid(duties):
    duty = duties[0]
    invalid_ids = ["not-a-uuid", "also-bad"]
    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_coins_to_duty(duty, invalid_ids)
    for bad_id in invalid_ids:
        assert bad_id in e.value.description
    assert e.value.code == 400


def test_attach_coins_nonexistent_coin(duties):
    duty = duties[0]
    fake_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_coins_to_duty(duty, fake_ids)
    for bad_id in fake_ids:
        assert bad_id in e.value.description
    assert e.value.code == 400


def test_attach_coins_non_list_input(duties):
    duty = duties[0]
    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_coins_to_duty(duty, "not-a-list")
    assert "'coin_ids' must be a list" in str(e.value)


def test_attach_coins_duplicate_ids(duties, coins):
    duty = duties[0]
    coin_id = str(coins[0].id)
    DutyHelper.attach_coins_to_duty(duty, [coin_id, coin_id])
    
    associated_coins = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == duty)]
    assert associated_coins.count(coins[0].id) == 1


def test_attach_coins_mixed_valid_and_invalid(duties, coins):
    duty = duties[0]
    valid_id = str(coins[0].id)
    invalid_ids = ["not-a-uuid", str(uuid.uuid4())]
    
    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_coins_to_duty(duty, [valid_id] + invalid_ids)
    
    for bad_id in invalid_ids:
        assert bad_id in e.value.description
    assert e.value.code == 400
    
    assert not DutyCoin.select().where(DutyCoin.coin == coins[0], DutyCoin.duty == duty).exists()


# ATTACH KSBS
def test_attach_ksbs_to_duty_creates_links(duties, ksbs):
    duty = duties[0]
    ksb_codes = [ksb.code for ksb in ksbs]

    DutyHelper.attach_ksbs_to_duty(duty, ksb_codes)

    for ksbs_item in ksbs:
        ksb = ksbs_item
        if isinstance(ksb, Knowledge):
            assert DutyKnowledge.select().where(DutyKnowledge.duty == duty, DutyKnowledge.knowledge == ksb).exists()
        elif isinstance(ksb, Skill):
            assert DutySkill.select().where(DutySkill.duty == duty, DutySkill.skill == ksb).exists()
        elif isinstance(ksb, Behaviour):
            assert DutyBehaviour.select().where(DutyBehaviour.duty == duty, DutyBehaviour.behaviour == ksb).exists()


def test_attach_ksbs_to_duty_ignores_invalid_codes(duties):
    duty = duties[0]
    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_ksbs_to_duty(duty, ["X999", "INB"])
    assert e.value.code == 400
    assert "Invalid KSB codes: X999, INB" in e.value.description

    assert DutyKnowledge.select().where(DutyKnowledge.duty == duty).count() == 0
    assert DutySkill.select().where(DutySkill.duty == duty).count() == 0
    assert DutyBehaviour.select().where(DutyBehaviour.duty == duty).count() == 0


def test_attach_ksbs_to_duty_mixed_valid_invalid(duties, ksbs):
    duty = duties[0]

    valid_code = ksbs[0].code
    invalid_codes = ["X999", "INB"]
    mixed_codes = [valid_code] + invalid_codes

    with pytest.raises(HTTPException) as e:
        DutyHelper.attach_ksbs_to_duty(duty, mixed_codes)

    assert e.value.code == 400
    assert "Invalid KSB codes: X999, INB" in e.value.description

    if isinstance(ksbs[0], Knowledge):
        assert DutyKnowledge.select().where(DutyKnowledge.duty == duty, DutyKnowledge.knowledge == ksbs[0]).exists()
    elif isinstance(ksbs[0], Skill):
        assert DutySkill.select().where(DutySkill.duty == duty, DutySkill.skill == ksbs[0]).exists()
    elif isinstance(ksbs[0], Behaviour):
        assert DutyBehaviour.select().where(DutyBehaviour.duty == duty, DutyBehaviour.behaviour == ksbs[0]).exists()

    assert DutyKnowledge.select().where(DutyKnowledge.duty == duty).count() + \
           DutySkill.select().where(DutySkill.duty == duty).count() + \
           DutyBehaviour.select().where(DutyBehaviour.duty == duty).count() == 1


# LIST ALL DUTIES
def test_list_all_duties_empty(duties):
    for duty in Duty.select():
        duty.delete_instance()
    result = DutyHelper.list_all_duties(full=False)
    assert result == []


def test_list_all_duties_returns_duties(duties):
    result = DutyHelper.list_all_duties(full=False)
    codes = [duty["code"] for duty in result]
    assert set(codes) == {duty.code for duty in duties}


# LIST ALL DUTIES WITH COINS AND KSBS
def test_list_all_duties_with_coins_and_ksbs(duties, coins, ksbs):
    duty = duties[0]
    DutyHelper.attach_coins_to_duty(duty, [str(coins[0].id), str(coins[1].id)])
    DutyHelper.attach_ksbs_to_duty(duty, [ksb.code for ksb in ksbs])

    result = DutyHelper.list_all_duties(full=True)

    serialized_duty = next(d for d in result if d["code"] == duty.code)
    coin_ids = [c["id"] for c in serialized_duty["coins"]]

    expected_ids = {str(coins[0].id), str(coins[1].id)}
    assert set(coin_ids) == expected_ids


def test_list_all_duties_with_coins_and_ksbs_empty():
    for duty in Duty.select():
        duty.delete_instance()
    result = DutyHelper.list_all_duties(full=True)
    assert result == []


# GET DUTY BY CODE
def test_get_duty_by_code_invalid_format():
    with pytest.raises(HTTPException) as e:
        DutyHelper.get_duty_by_code("X1")
    assert e.value.code == 400


def test_get_duty_by_code_not_found():
    with pytest.raises(HTTPException) as e:
        DutyHelper.get_duty_by_code("D999")
    assert e.value.code == 404


def test_get_duty_by_code_with_coins_success(duties, coins):
    duty = duties[0]
    DutyHelper.attach_coins_to_duty(duty, [str(coins[0].id)])
    result = DutyHelper.get_duty_by_code(duty.code)
    assert result["code"] == duty.code
    assert len(result["coins"]) == 1


def test_get_duty_by_code_with_coins_and_ksbs_success(duties, coins, ksbs):
    duty = duties[0]
    DutyHelper.attach_coins_to_duty(duty, [str(coins[0].id)])
    DutyHelper.attach_ksbs_to_duty(duty, [ksbs[0].code])

    result = DutyHelper.get_duty_by_code(duty.code)
    assert result["code"] == duty.code
    assert len(result["coins"]) == 1
    assert result["coins"][0]["id"] == str(coins[0].id)


# CREATE DUTY
def test_create_duty_missing_body():
    with pytest.raises(HTTPException) as e:
        DutyHelper.create_duty(None)
    assert e.value.code == 400


def test_create_duty_missing_fields():
    with pytest.raises(HTTPException) as e:
        DutyHelper.create_duty({"code": "D10"})
    assert e.value.code == 400


def test_create_duty_with_coins(coins):
    data = {
        "code": "D100",
        "name": "Test Duty",
        "description": "Test Description",
        "coin_ids": [str(coins[0].id)]
    }
    duty = DutyHelper.create_duty(data)
    assert duty.code == "D100"
    attached = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == duty)]
    assert attached == [coins[0].id]


# UPDATE DUTY
def test_update_duty_not_found():
    with pytest.raises(HTTPException) as e:
        DutyHelper.update_duty("D999", {"name": "New Duty Name"})
    assert e.value.code == 404


def test_update_duty_success(duties, coins):
    duty = duties[0]
    data = {
        "name": "Updated Duty Name",
        "description": "Updated Duty Description",
        "coin_ids": [str(coins[0].id)]
    }
    updated = DutyHelper.update_duty(duty.code, data)
    assert updated.name == "Updated Duty Name"
    attached = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == updated)]
    assert attached == [coins[0].id]


def test_update_duty_change_code_unique(duty_with_coins):
    old_code = duty_with_coins.code
    new_code = "D999"
    
    updated = DutyHelper.update_duty(old_code, {"code": new_code})
    assert updated.code == new_code
    with pytest.raises(Duty.DoesNotExist):
        Duty.get(Duty.code == old_code)


def test_update_duty_name_without_coin_ids_preserves_existing_coins(duty_with_coins):
    updated_duty = DutyHelper.update_duty(duty_with_coins.code, {"name": "Updated Duty Name"})
    
    associated_coin_ids = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == updated_duty)]
    
    original_coin_ids = [dc.coin.id for dc in DutyCoin.select().where(DutyCoin.duty == duty_with_coins)]
    
    assert associated_coin_ids == original_coin_ids


# DELETE DUTY
def test_delete_duty_not_found():
    with pytest.raises(HTTPException) as e:
        DutyHelper.delete_duty("D999")
    assert e.value.code == 404


def test_delete_duty_success(duty_with_coins):
    DutyHelper.delete_duty(duty_with_coins.code)

    with pytest.raises(Duty.DoesNotExist):
        Duty.get(Duty.code == duty_with_coins.code)
    assert DutyCoin.select().where(DutyCoin.duty == duty_with_coins).count() == 0


def test_delete_duty_without_coins(duties):
    duty = duties[0]
    DutyCoin.delete().where(DutyCoin.duty == duty).execute()
    
    DutyHelper.delete_duty(duty.code)
    with pytest.raises(Duty.DoesNotExist):
        Duty.get(Duty.code == duty.code)