def test_admin_duties_page_loads(mocker, logged_in_admin_user, mocked_duties):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    client = logged_in_admin_user
    response = client.get("/admin/duties")
    html = response.data.decode()

    assert response.status_code == 200

    for duty in mocked_duties:
        assert duty.code in html
        assert duty.name in html
        assert duty.description in html

        if duty.coins:
            for coin in duty.coins:
                assert coin["name"] in html

        if hasattr(duty, "ksbs") and duty.ksbs:
            for ksb in duty.ksbs:
                assert ksb in html