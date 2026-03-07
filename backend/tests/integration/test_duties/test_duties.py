import uuid

# GET DUTIES V1
def test_get_duties_returns_all_duties(client, duties):
    response = client.get("/v1/duties")
    data = response.json

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert len(data) == len(duties)
    assert isinstance(data, list)

    returned_names = {duty["name"] for duty in data}
    for duty in duties:
        assert duty.name in returned_names


def test_duties_have_id_code_name_and_description(client, duties):
    response = client.get("/v1/duties")
    data = response.json

    for duty in data:
        assert set(duty.keys()) == {"id", "code", "name", "description"}


def test_get_duties_returns_correct_duty_descriptions_and_codes(client, duties):
    response = client.get("/v1/duties")
    data = response.json

    duty_map = {duty.code: duty for duty in duties}

    for duty in data:
        assert duty["code"] in duty_map
        expected_duty = duty_map[duty["code"]]
        assert duty["name"] == expected_duty.name
        assert duty["description"] == expected_duty.description


def test_duties_have_non_integer_id(client, duties):
    response = client.get("/v1/duties")
    data = response.json

    for duty in data:
        assert isinstance(duty["id"], str)
        uuid.UUID(duty["id"])


def test_get_duties_has_no_duplicates(client, duties):
    response = client.get("/v1/duties")
    data = response.json

    duty_codes = [duty["code"] for duty in data]
    assert len(duty_codes) == len(set(duty_codes))

# GET DUTIES V2
def test_get_duties_v2_duties_include_coins_and_ksbs(client, duties, coins, ksbs):
    duty = duties[0]
    from helpers.duty import DutyHelper
    DutyHelper.attach_coins_to_duty(duty, [str(coins[0].id), str(coins[1].id)])
    DutyHelper.attach_ksbs_to_duty(duty, [ksb.code for ksb in ksbs])

    response = client.get("/v2/duties")
    data = response.json

    serialized_duty = next(d for d in data if d["code"] == duty.code)

    assert "coins" in serialized_duty
    coin_ids = [c["id"] for c in serialized_duty["coins"]]
    expected_ids = {str(coins[0].id), str(coins[1].id)}
    assert set(coin_ids) == expected_ids

    assert "ksbs" in serialized_duty
    ksb_codes = serialized_duty["ksbs"]
    expected_ksb_codes = {ksb.code for ksb in ksbs}
    assert set(ksb_codes) == expected_ksb_codes


def test_get_duties_v2_empty_coins_and_ksbs(client, duties):
    duty = duties[1] 
    from models import DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour
    DutyCoin.delete().where(DutyCoin.duty == duty).execute()
    DutyKnowledge.delete().where(DutyKnowledge.duty == duty).execute()
    DutySkill.delete().where(DutySkill.duty == duty).execute()
    DutyBehaviour.delete().where(DutyBehaviour.duty == duty).execute()

    response = client.get("/v2/duties")
    data = response.json

    serialized_duty = next(d for d in data if d["code"] == duty.code)

    assert serialized_duty["coins"] == []
    assert serialized_duty["ksbs"] == []