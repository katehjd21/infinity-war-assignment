import uuid
from models import Duty, Coin, Knowledge, Skill, Behaviour, DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour

# POST DUTY
def test_post_duty_creates_duty(client):
    response = client.post("/duties", json={
        "code": "D99",
        "name": "New Duty",
        "description": "New Duty Description."
    })

    data = response.json

    assert response.status_code == 201
    assert response.content_type == "application/json"
    assert data["code"] == "D99"
    assert data["name"] == "New Duty"
    assert data["description"] == "New Duty Description."
    uuid.UUID(data["id"])


def test_post_duty_with_coins_success(client, coins):
    response = client.post("/duties", json={
        "code": "D101",
        "name": "Duty with KSBs",
        "description": "Duty description.",
        "coin_ids": [coin.id for coin in coins]
    })

    data = response.json
    assert response.status_code == 201
    assert data["code"] == "D101"

    duty = Duty.get(Duty.code == "D101")
    for coin in coins:
        if isinstance(coin, Coin):
            assert DutyCoin.select().where(DutyCoin.duty == duty, DutyCoin.coin == coin).exists()


def test_post_duty_with_ksbs_success(client, ksbs):
    response = client.post("/duties", json={
        "code": "D101",
        "name": "Duty with KSBs",
        "description": "Duty description.",
        "ksb_codes": [ksb.code for ksb in ksbs]
    })

    data = response.json
    assert response.status_code == 201
    assert data["code"] == "D101"

    duty = Duty.get(Duty.code == "D101")

    for ksbs_item in ksbs:
        ksb = ksbs_item
        if isinstance(ksb, Knowledge):
            assert DutyKnowledge.select().where(DutyKnowledge.duty == duty, DutyKnowledge.knowledge == ksb).exists()
        elif isinstance(ksb, Skill):
            assert DutySkill.select().where(DutySkill.duty == duty, DutySkill.skill == ksb).exists()
        elif isinstance(ksb, Behaviour):
            assert DutyBehaviour.select().where(DutyBehaviour.duty == duty, DutyBehaviour.behaviour == ksb).exists()


def test_post_duty_with_coins_and_ksbs_success(client, coins, ksbs):
    response = client.post("/duties", json={
        "code": "D101",
        "name": "Duty with KSBs",
        "description": "Duty description.",
        "coin_ids": [coin.id for coin in coins],
        "ksb_codes": [ksb.code for ksb in ksbs]
    })

    data = response.json
    assert response.status_code == 201
    assert data["code"] == "D101"

    duty = Duty.get(Duty.code == "D101")

    for coin in coins:
        if isinstance(coin, Coin):
            assert DutyCoin.select().where(DutyCoin.duty == duty, DutyCoin.coin == coin).exists()
            
    for ksbs_item in ksbs:
        ksb = ksbs_item
        if isinstance(ksb, Knowledge):
            assert DutyKnowledge.select().where(DutyKnowledge.duty == duty, DutyKnowledge.knowledge == ksb).exists()
        elif isinstance(ksb, Skill):
            assert DutySkill.select().where(DutySkill.duty == duty, DutySkill.skill == ksb).exists()
        elif isinstance(ksb, Behaviour):
            assert DutyBehaviour.select().where(DutyBehaviour.duty == duty, DutyBehaviour.behaviour == ksb).exists()


def test_post_duty_returns_400_if_body_missing(client):
    response = client.post("/duties", json={})

    assert response.status_code == 400
    assert response.json["description"] == "Request body missing."


def test_post_duty_returns_400_if_missing_code(client):
    response = client.post("/duties", json={
        "name": "Missing Code Duty",
        "description": "Missing Code Duty Description"
    })

    assert response.status_code == 400
    assert response.json["description"] == "Missing 'code' key in request body."


def test_post_duty_returns_400_if_invalid_code_format(client):
    response = client.post("/duties", json={
        "code": "INVALID",
        "name": "Invalid Duty Code",
        "description": "Invalid Duty Code Description"
    })

    assert response.status_code == 400
    assert "Invalid Duty Code format" in response.json["description"]


def test_post_duty_returns_400_if_duplicate_code(client, duty_with_coins):
    response = client.post("/duties", json={
        "code": duty_with_coins.code,
        "name": "Another Duty Name",
        "description": "Another Duty Name Description"
    })

    assert response.status_code == 400
    assert response.json["description"] == "Duty code already exists."


def test_post_duty_returns_400_if_duplicate_name(client, duty_with_coins):
    response = client.post("/duties", json={
        "code": "D100",
        "name": duty_with_coins.name,
        "description": "Duplicate Duty Description"
    })

    assert response.status_code == 400
    assert response.json["description"] == "Duty name already exists."