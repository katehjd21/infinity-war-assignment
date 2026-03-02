# DELETE DUTY V1
def test_delete_duty_removes_duty_from_database(client, duty_with_coins):
    response = client.delete(f"/v1/duties/{duty_with_coins.code}")

    assert response.status_code == 200
    assert response.json["message"] == "Duty has been successfully deleted!"


def test_delete_duty_returns_404_if_not_found(client):
    response = client.delete("/v1/duties/D999")

    assert response.status_code == 404
    assert response.json["description"] == "Duty not found."


def test_delete_duty_returns_400_if_invalid_duty_code(client):
    response = client.delete("/v1/duties/INVALID")

    assert response.status_code == 400
    assert "Invalid Duty Code format" in response.json["description"]


# DELETE DUTY V2
def test_delete_duty_v2_removes_duty_from_database_if_admin_user(logged_in_admin, client, duty_with_ksbs):
    response = logged_in_admin.delete(f"/v2/duties/{duty_with_ksbs.code}")

    assert response.status_code == 200
    assert response.json["message"] == "Duty has been successfully deleted!"

    get_response = client.get(f"/duties/{duty_with_ksbs.code}")
    assert get_response.status_code == 404


def test_delete_duty_v2_does_not_remove_duty_from_database_if_unauthenticated_user(client, duty_with_ksbs):
    response = client.delete(f"/v2/duties/{duty_with_ksbs.code}")

    assert response.status_code == 401

    get_response = client.get(f"/duties/{duty_with_ksbs.code}")
    assert get_response.status_code == 200


def test_delete_duty_v2_does_not_remove_duty_from_database_if_authenticated_user(logged_in_authenticated_user, client, duty_with_ksbs):
    response = logged_in_authenticated_user.delete(f"/v2/duties/{duty_with_ksbs.code}")

    assert response.status_code == 403

    get_response = client.get(f"/duties/{duty_with_ksbs.code}")
    assert get_response.status_code == 200