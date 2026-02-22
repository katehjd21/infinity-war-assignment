def test_single_duty_page_get(mocker, client, mocked_duty):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=mocked_duty)

    response = client.get(f'/duties/{mocked_duty.code}')
    html = response.data.decode()

    assert response.status_code == 200
    assert mocked_duty.code in html
    assert mocked_duty.name in html
    assert mocked_duty.description in html

    for coin in mocked_duty.coins:
        assert coin["name"] in html


def test_single_duty_page_not_found(mocker, client):
    mocker.patch("controllers.duty_controller.DutyController.fetch_duty", return_value=None)

    response = client.get('/duties/non-existent-code')

    assert response.status_code == 404