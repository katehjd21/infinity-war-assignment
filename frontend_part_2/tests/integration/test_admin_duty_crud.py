def test_admin_create_duty_flash_success(mocker, logged_in_admin_user, mocked_coins):
    client = logged_in_admin_user
    mocker.patch(
        "controllers.duty_controller.DutyController.create_duty",
        return_value=("new_duty_obj", None)
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = client.post(
        "/admin/duties/create",
        data={
            "code": "D99",
            "name": "Test Duty",
            "description": "Description for test duty",
            "coin_ids": [c.id for c in mocked_coins[:2]],
            "ksb_codes": "K1,K2"
        },
        follow_redirects=True
    )

    html = response.data.decode()
    assert "Duty created successfully." in html
    assert response.status_code == 200

def test_admin_edit_duty_flash_success(mocker, logged_in_admin_user, mocked_duties, mocked_coins):
    client = logged_in_admin_user
    duty_code = mocked_duties[0].code

    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_duty",
        return_value=mocked_duties[0]
    )
    mocker.patch(
        "controllers.duty_controller.DutyController.update_duty",
        return_value=("updated_duty_obj", None)
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = client.post(
        f"/admin/duties/{duty_code}/edit",
        data={
            "name": "Updated Name",
            "description": "Updated description",
            "coin_ids": [c.id for c in mocked_coins[:1]],
            "ksb_codes": "K1,K2"
        },
        follow_redirects=True
    )

    html = response.data.decode()
    assert "Duty updated successfully." in html
    assert response.status_code == 200


def test_admin_delete_duty_flash_success(mocker, logged_in_admin_user):
    client = logged_in_admin_user
    duty_code = "D99"

    mocker.patch(
        "controllers.duty_controller.DutyController.delete_duty",
        return_value=True
    )

    response = client.post(
        f"/admin/duties/{duty_code}/delete",
        follow_redirects=True
    )

    html = response.data.decode()
    assert "Duty deleted successfully." in html
    assert response.status_code == 200