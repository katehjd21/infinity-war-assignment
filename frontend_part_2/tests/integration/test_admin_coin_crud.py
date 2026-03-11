# ADMIN CREATE COIN
def test_admin_create_coin_page_renders(logged_in_admin_user):
    response = logged_in_admin_user.get("/admin/coins/create")

    html = response.data.decode()

    assert response.status_code == 200
    assert "Create Coin" in html


def test_admin_create_coin_calls_coin_controller(mocker, logged_in_admin_user):
    mock_create = mocker.patch(
        "controllers.coin_controller.CoinController.create_coin",
        return_value=("coin_obj", None)
    )

    logged_in_admin_user.post(
        "/admin/coins/create",
        data={
            "name": "Test Coin",
            "duty_codes": "D1,D2",
            "completed": "on"
        }
    )

    mock_create.assert_called_once_with(
        "Test Coin",
        duty_codes=["D1", "D2"],
        completed=True
    )


def test_admin_create_coin_success(mocker, logged_in_admin_user):
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


def test_admin_create_coin_error(mocker, logged_in_admin_user):
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


# ADMIN UPDATE COIN
def test_admin_edit_coin_page_renders(mocker, logged_in_admin_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    response = logged_in_admin_user.get("/admin/coins/11111111-1111-1111-1111-111111111111/edit")

    html = response.data.decode()

    assert response.status_code == 200
    assert "Edit Coin" in html


def test_admin_edit_coin_success(mocker, logged_in_admin_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    mocker.patch(
        "controllers.coin_controller.CoinController.update_coin",
        return_value=("updated_coin", None)
    )

    response = logged_in_admin_user.post(
        "/admin/coins/11111111-1111-1111-1111-111111111111/edit",
        data={
            "name": "Updated Coin",
            "duty_codes": "D1,D2",
            "completed": "on"
        },
        follow_redirects=True
    )

    html = response.data.decode()

    assert response.status_code == 200
    assert "Coin updated successfully." in html


def test_admin_edit_coin_calls_fetch_controller(mocker, logged_in_admin_user, mocked_coin):
    mock_fetch = mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    logged_in_admin_user.get("/admin/coins/11111111-1111-1111-1111-111111111111/edit")

    mock_fetch.assert_called_once_with("11111111-1111-1111-1111-111111111111")


def test_admin_edit_coin_calls_update_controller(mocker, logged_in_admin_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    mock_update = mocker.patch(
        "controllers.coin_controller.CoinController.update_coin",
        return_value=("updated_coin", None)
    )

    logged_in_admin_user.post(
        "/admin/coins/11111111-1111-1111-1111-111111111111/edit",
        data={
            "name": "Updated Coin",
            "duty_codes": "D1,D2",
            "completed": "on"
        }
    )

    mock_update.assert_called_once_with(
        "11111111-1111-1111-1111-111111111111",
        name="Updated Coin",
        duty_codes=["D1", "D2"],
        completed=True
    )


def test_admin_edit_coin_error(mocker, logged_in_admin_user, mocked_coin):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=mocked_coin
    )

    mocker.patch(
        "controllers.coin_controller.CoinController.update_coin",
        return_value=(None, "Update failed")
    )

    response = logged_in_admin_user.post(
        "/admin/coins/11111111-1111-1111-1111-111111111111/edit",
        data={"name": "Fail Coin"},
        follow_redirects=True
    )

    html = response.data.decode()

    assert "Update failed" in html


def test_admin_edit_coin_not_found(mocker, logged_in_admin_user):
    mocker.patch(
        "controllers.coin_controller.CoinController.fetch_coin_by_id",
        return_value=None
    )

    response = logged_in_admin_user.get("/admin/coins/999/edit")

    assert response.status_code == 404
    assert "Coin not found" in response.data.decode()


# ADMIN DELETE COIN
def test_admin_delete_coin_success(mocker, logged_in_admin_user):
    mocker.patch(
        "controllers.coin_controller.CoinController.delete_coin",
        return_value=True
    )

    response = logged_in_admin_user.post(
        "/admin/coins/11111111-1111-1111-1111-111111111111/delete",
        follow_redirects=True
    )

    html = response.data.decode()

    assert response.status_code == 200
    assert "Coin deleted successfully." in html


def test_admin_delete_coin_calls_controller(mocker, logged_in_admin_user):
    mock_delete = mocker.patch(
        "controllers.coin_controller.CoinController.delete_coin",
        return_value=True
    )

    logged_in_admin_user.post("/admin/coins/11111111-1111-1111-1111-111111111111/delete")

    mock_delete.assert_called_once_with("11111111-1111-1111-1111-111111111111")


def test_admin_delete_coin_failure(mocker, logged_in_admin_user):
    mocker.patch(
        "controllers.coin_controller.CoinController.delete_coin",
        return_value=False
    )

    response = logged_in_admin_user.post("/admin/coins/11111111-1111-1111-1111-111111111111/delete")

    assert response.status_code == 500
    assert "Failed to delete coin" in response.data.decode()