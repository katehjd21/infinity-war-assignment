# DELETE DUTY
def test_delete_duty_removes_duty_from_database(client, duty_with_coins):
    response = client.delete(f"/duties/{duty_with_coins.code}")

    assert response.status_code == 200
    assert response.json["message"] == "Duty has been successfully deleted!"


def test_delete_duty_returns_404_if_not_found(client):
    response = client.delete("/duties/D999")

    assert response.status_code == 404
    assert response.json["description"] == "Duty not found."


def test_delete_duty_returns_400_if_invalid_duty_code(client):
    response = client.delete("/duties/INVALID")

    assert response.status_code == 400
    assert "Invalid Duty Code format" in response.json["description"]