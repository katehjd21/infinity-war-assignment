# ADMIN CREATE DUTY
def test_admin_create_duty_page_renders(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = logged_in_admin_user.get("/admin/duties/create")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Create Duty</h1>" in html
    for coin in mocked_coins:
        assert coin.name in html


def test_admin_create_duty_success(mocker, logged_in_admin_user, mocked_coins, mocked_duties):
    mocker.patch("utils.helpers.login_api_session", return_value={"role": "admin"})
    mocker.patch(
        "controllers.duty_controller.DutyController.create_duty",
        return_value=("new_duty_obj", None)
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    response = logged_in_admin_user.post(
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


def test_admin_create_duty_backend_error(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )
    mocker.patch(
        "controllers.duty_controller.DutyController.create_duty",
        return_value=(None, "Duplicate duty code")
    )

    response = logged_in_admin_user.post(
        "/admin/duties/create",
        data={
            "code": "D1",
            "name": "Duty 1",
            "description": "Description",
            "coin_ids": [c.id for c in mocked_coins[:2]],
            "ksb_codes": "K1,K2"
        }
    )

    html = response.data.decode()
    assert response.status_code == 200
    assert "Duplicate duty code" in html
    assert "<h1>Edit Duty</h1>" in html



# ADMIN EDIT DUTY
def test_admin_edit_duty_page_renders(mocker, logged_in_admin_user, mocked_duties, mocked_coins):
    duty = mocked_duties[0]
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_duty",
        return_value=duty
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = logged_in_admin_user.get(f"/admin/duties/{duty.code}/edit")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<h1>Edit Duty</h1>" in html
    assert duty.name in html
    assert duty.description in html
    for coin in mocked_coins:
        assert coin.name in html


def test_admin_edit_duty_success(mocker, logged_in_admin_user, mocked_duties, mocked_coins):
    duty_code = mocked_duties[0].code

    mocker.patch("utils.helpers.login_api_session", return_value={"role": "admin"})

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

    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    response = logged_in_admin_user.post(
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


def test_admin_edit_duty_backend_error(mocker, logged_in_admin_user, mocked_duties, mocked_coins):
    duty = mocked_duties[0]
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_duty",
        return_value=duty
    )
    mocker.patch(
        "controllers.duty_controller.DutyController.update_duty",
        return_value=(None, "Update failed")
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = logged_in_admin_user.post(
        f"/admin/duties/{duty.code}/edit",
        data={
            "name": "New Name",
            "description": "New description",
            "coin_ids": [c.id for c in mocked_coins[:1]],
            "ksb_codes": "K1,K2"
        }
    )

    html = response.data.decode()
    assert response.status_code == 200
    assert "Update failed" in html
    assert "<h1>Edit Duty</h1>" in html


def test_admin_edit_duty_not_found(mocker, logged_in_admin_user, mocked_coins):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_duty",
        return_value=None
    )
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_all_coins",
        return_value=mocked_coins
    )

    response = logged_in_admin_user.get("/admin/duties/INVALIDCODE/edit")
    assert response.status_code == 404
    assert "Duty not found" in response.data.decode()


# ADMIN DELETE DUTY
def test_admin_delete_duty_success(mocker, logged_in_admin_user, mocked_duties):
    duty_code = "D99"

    mocker.patch("utils.helpers.login_api_session", return_value={"role": "admin"})

    mocker.patch(
        "controllers.duty_controller.DutyController.delete_duty",
        return_value=True
    )

    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    response = logged_in_admin_user.post(
        f"/admin/duties/{duty_code}/delete",
        follow_redirects=True
    )

    html = response.data.decode()
    assert "Duty deleted successfully." in html
    assert response.status_code == 200


def test_admin_delete_duty_failure(mocker, logged_in_admin_user):
    duty_code = "D1"
    mocker.patch(
        "controllers.duty_controller.DutyController.delete_duty",
        return_value=False
    )

    response = logged_in_admin_user.post(f"/admin/duties/{duty_code}/delete")
    html = response.data.decode()

    assert response.status_code == 500
    assert "Failed to delete duty" in html