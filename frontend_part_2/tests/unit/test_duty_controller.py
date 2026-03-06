import pytest
from controllers.duty_controller import DutyController
from models.duty import Duty

@pytest.fixture
def duty_controller():
    return DutyController()


# FETCH DUTY
def test_duty_controller_fetch_success(mocker, duty_controller, mocked_duty):
    mocker.patch("models.duty.Duty.fetch_duty_from_backend", return_value=mocked_duty)
    result = duty_controller.fetch_duty(mocked_duty.code)
    assert result == mocked_duty


def test_duty_controller_fetch_not_found(mocker, duty_controller):
    mocker.patch("models.duty.Duty.fetch_duty_from_backend", return_value=None)
    result = duty_controller.fetch_duty("D99")
    assert result is None


# CREATE DUTY 
def test_duty_controller_create_success(mocker, duty_controller, mocked_duty):
    mocker.patch("models.duty.Duty.create_duty", return_value=mocked_duty)
    result = duty_controller.create_duty(
        code=mocked_duty.code,
        name=mocked_duty.name,
        description=mocked_duty.description
    )
    assert result == mocked_duty


def test_duty_controller_create_failure(mocker, duty_controller):
    mocker.patch("models.duty.Duty.create_duty", return_value=None)
    result = duty_controller.create_duty("D1", "Fail Duty", "Fail Desc")
    assert result is None


# UPDATE DUTY
def test_duty_controller_update_success(mocker, duty_controller, mocked_duty):
    updated_duty = mocked_duty
    updated_duty.name = "Updated Name"
    mocker.patch("models.duty.Duty.update_duty", return_value=updated_duty)
    result = duty_controller.update_duty(code=mocked_duty.code, name="Updated Name")
    assert result.name == "Updated Name"


def test_duty_controller_update_failure(mocker, duty_controller):
    mocker.patch("models.duty.Duty.update_duty", return_value=None)
    result = duty_controller.update_duty("D99", name="Fail Update")
    assert result is None


# DELETE DUTY
def test_duty_controller_delete_success(mocker, duty_controller):
    mocker.patch("models.duty.Duty.delete_duty", return_value=True)
    result = duty_controller.delete_duty("D1")
    assert result is True


def test_duty_controller_delete_failure(mocker, duty_controller):
    mocker.patch("models.duty.Duty.delete_duty", return_value=False)
    result = duty_controller.delete_duty("D99")
    assert result is False