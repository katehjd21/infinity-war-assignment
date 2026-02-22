import pytest
from models.duty import Duty
from controllers.duty_controller import DutyController
 
@pytest.fixture
def duty_controller():
    return DutyController()

def test_duty_controller_can_fetch_duty_by_duty_code(mocker, duty_controller, mocked_duty):
    mocker.patch("models.duty.Duty.fetch_duty_from_backend", return_value=mocked_duty)
    fetched_duty = duty_controller.fetch_duty("D1")

    assert fetched_duty.name == "Duty 1"
    assert fetched_duty.description == "Duty 1 Description"

    expected_coins = [{"name": "Automate"}, {"name": "Houston"}]

    assert fetched_duty.coins == expected_coins

