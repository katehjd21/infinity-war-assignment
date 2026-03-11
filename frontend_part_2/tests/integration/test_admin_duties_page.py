from models.duty import Duty

def test_admin_duties_page_renders(mocker, logged_in_admin_user, mocked_duties):
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


def test_admin_duties_page_with_no_duties(mocker, logged_in_admin_user):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=[]
    )

    response = logged_in_admin_user.get("/admin/duties")
    html = response.data.decode()

    assert response.status_code == 200
    assert "<tbody>" in html
    assert "Edit" not in html
    assert "Delete" not in html


def test_admin_duties_page_links(mocker, logged_in_admin_user, mocked_duties):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    response = logged_in_admin_user.get("/admin/duties")
    html = response.data.decode()

    assert 'href="/admin/duties/create"' in html
    assert 'href="/"' in html or 'Back to Coins' in html

    for duty in mocked_duties:
        assert f'/admin/duties/{duty.code}/edit' in html
        assert f'/admin/duties/{duty.code}/delete' in html


def test_admin_duties_page_shows_none_for_empty_fields(mocker, logged_in_admin_user):
    empty_duty = Duty(code="D0", name="Duty 0", description="No coins or KSBs", coins=[], ksbs=[])
    mocker.patch("controllers.duty_controller.DutyController.fetch_all_duties", return_value=[empty_duty])

    response = logged_in_admin_user.get("/admin/duties")
    html = response.data.decode()

    assert "None" in html


def test_admin_duties_page_redirect_authenticated_user(logged_in_authenticated_user, mocker, mocked_duties):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        return_value=mocked_duties
    )

    response = logged_in_authenticated_user.get("/admin/duties", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "You do not have permission to access this page." in html
    assert "<h1>Apprenticeship Coins</h1>" in html


def test_admin_duties_page_redirect_unauthenticated_user(client):
    response = client.get("/admin/duties", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "You must be logged in to access this page." in html
    assert "<h1>Login</h1>" in html


def test_admin_duties_page_backend_failure(mocker, logged_in_admin_user):
    mocker.patch(
        "controllers.duty_controller.DutyController.fetch_all_duties",
        side_effect=Exception("Session expired")
    )

    response = logged_in_admin_user.get("/admin/duties", follow_redirects=True)
    html = response.data.decode()

    assert response.status_code == 200
    assert "Your session has expired. Please log in again." in html
    assert "<h1>Login</h1>" in html
