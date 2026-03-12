import pytest
from controllers.duty_controller import DutyController

@pytest.fixture
def duty_controller():
    return DutyController()


# FETCH ALL DUTIES
def test_duty_controller_fetch_all_duties(mocker, duty_controller, mocked_duties):
    mocker.patch("models.duty.Duty.fetch_duties_from_backend", return_value=mocked_duties)
    result = duty_controller.fetch_all_duties()
    assert result == mocked_duties


def test_duty_controller_fetch_all_duties_empty(mocker, duty_controller):
    mocker.patch("models.duty.Duty.fetch_duties_from_backend", return_value=[])
    result = duty_controller.fetch_all_duties()
    assert result == []


# FETCH DUTY
def test_duty_controller_fetch_duty_success(mocker, duty_controller, mocked_duty):
    mocker.patch("models.duty.Duty.fetch_duty_from_backend", return_value=mocked_duty)
    result = duty_controller.fetch_duty(mocked_duty.code)
    assert result == mocked_duty


def test_duty_controller_fetch_duty_not_found(mocker, duty_controller):
    mocker.patch("models.duty.Duty.fetch_duty_from_backend", return_value=None)
    result = duty_controller.fetch_duty("D99")
    assert result is None


# CREATE DUTY
def test_duty_controller_create_duty_returns_tuple(mocker, duty_controller, mocked_duty):
    mocker.patch("models.duty.Duty.create_duty", return_value=(mocked_duty, None))
    result = duty_controller.create_duty(code=mocked_duty.code, name=mocked_duty.name, description=mocked_duty.description)
    assert isinstance(result, tuple)
    duty, error = result
    assert duty == mocked_duty
    assert error is None


def test_duty_controller_create_duty_failure_returns_tuple(mocker, duty_controller):
    mocker.patch("models.duty.Duty.create_duty", return_value=(None, "Server error"))
    result = duty_controller.create_duty("D1", "Fail Duty", "Fail Desc")
    duty, error = result
    assert duty is None
    assert error == "Server error"


# UPDATE DUTY
def test_duty_controller_update_duty_returns_tuple(mocker, duty_controller, mocked_duty):
    updated_duty = mocked_duty
    updated_duty.name = "Updated Name"
    mocker.patch("models.duty.Duty.update_duty", return_value=(updated_duty, None))
    result = duty_controller.update_duty(code=mocked_duty.code, name="Updated Name")
    assert isinstance(result, tuple)
    duty, error = result
    assert duty.name == "Updated Name"
    assert error is None


def test_duty_controller_update_duty_failure_returns_tuple(mocker, duty_controller):
    mocker.patch("models.duty.Duty.update_duty", return_value=(None, "Server error"))
    result = duty_controller.update_duty("D99", name="Fail Update")
    duty, error = result
    assert duty is None
    assert error == "Server error"


# DELETE DUTY
def test_duty_controller_delete_duty_success(mocker, duty_controller):
    mocker.patch("models.duty.Duty.delete_duty", return_value=True)
    result = duty_controller.delete_duty("D1")
    assert result is True


def test_duty_controller_delete_duty_failure(mocker, duty_controller):
    mocker.patch("models.duty.Duty.delete_duty", return_value=False)
    result = duty_controller.delete_duty("D99")
    assert result is False