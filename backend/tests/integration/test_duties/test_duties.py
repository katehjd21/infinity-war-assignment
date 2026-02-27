import uuid

# GET DUTIES
def test_get_duties_returns_all_duties(client, duties):
    response = client.get("/duties")
    data = response.json

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert len(data) == len(duties)
    assert isinstance(data, list)

    returned_names = {duty["name"] for duty in data}
    for duty in duties:
        assert duty.name in returned_names


def test_duties_have_id_code_name_and_description(client, duties):
    response = client.get("/duties")
    data = response.json

    for duty in data:
        assert set(duty.keys()) == {"id", "code", "name", "description"}


def test_get_duties_returns_correct_duty_descriptions_and_codes(client, duties):
    response = client.get("/duties")
    data = response.json

    duty_map = {duty.code: duty for duty in duties}

    for duty in data:
        assert duty["code"] in duty_map
        expected_duty = duty_map[duty["code"]]
        assert duty["name"] == expected_duty.name
        assert duty["description"] == expected_duty.description


def test_duties_have_non_integer_id(client, duties):
    response = client.get("/duties")
    data = response.json

    for duty in data:
        assert isinstance(duty["id"], str)
        uuid.UUID(duty["id"])


def test_get_duties_has_no_duplicates(client, duties):
    response = client.get("/duties")
    data = response.json

    duty_codes = [duty["code"] for duty in data]
    assert len(duty_codes) == len(set(duty_codes))


