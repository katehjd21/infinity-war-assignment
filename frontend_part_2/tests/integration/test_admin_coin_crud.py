def test_admin_create_coin_flash_success(mocker, logged_in_admin_user):
    client = logged_in_admin_user
    mocker.patch(
        "controllers.coin_controller.CoinController.create_coin",
        return_value=("new_coin_obj", None)
    )

    response = client.post(
        "/admin/coins/create",
        data={"name": "New Coin", "duty_codes": "D1,D2"},
        follow_redirects=True
    )
    html = response.data.decode()
    assert "Coin created successfully." in html
    assert response.status_code == 200


def test_admin_create_coin_error_flash(mocker, logged_in_admin_user):
    client = logged_in_admin_user
    mocker.patch(
        "controllers.coin_controller.CoinController.create_coin",
        return_value=(None, "Server error")
    )

    response = client.post(
        "/admin/coins/create",
        data={"name": "Fail Coin", "duty_codes": ""},
        follow_redirects=True
    )
    html = response.data.decode()
    assert "Server error" in html