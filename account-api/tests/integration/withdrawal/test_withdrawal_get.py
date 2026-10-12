from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import values_of
from tests.utils.mock_generator import FeeApiMock, SpiApiMock
from tests.utils.mock_utils import Mock


def withdraw(client_key: str, account_key: str, amount: str = "30.00") -> tuple:
    payload = PayloadGenerator.create_withdrawal_payload(amount=amount)
    _status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)

    return payload, response


def open_account_with_balance(amount: str) -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]
    ObjectGenerator.create_deposit(client_key, account_key, amount=amount)

    return client_key, account_key


class TestWithdrawalGet:

    def test_gets_completed_withdrawal(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(client_key)

        payload, response = withdraw(client_key, account_key, amount="30")
        withdrawal_key = response["withdrawal_key"]

        status, response = RequestGenerator.GET_withdrawal(client_key, withdrawal_key)
        assert status == 200

        created_at = response["created_at"]
        event_dates = values_of(response["status_events"], "created_at")
        assert created_at is not None
        assert len(event_dates) == 3

        assert response == {
            "withdrawal_key": withdrawal_key,
            "amount": "30.00",
            "status": "completed",
            "receiver_data": payload["receiver_data"],
            "status_events": [
                {"status": "pending_confirmation", "created_at": event_dates[0]},
                {"status": "pending_fee", "created_at": event_dates[1]},
                {"status": "completed", "created_at": event_dates[2]},
            ],
            "created_at": created_at,
        }

    def test_shows_pending_fee(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee_not_found(client_key)

        _payload, response = withdraw(client_key, account_key)
        assert response["status"] == "completed"

        status, response = RequestGenerator.GET_withdrawal(client_key, response["withdrawal_key"])
        assert status == 200
        assert response["status"] == "pending_fee"
        assert values_of(response["status_events"], "status") == ["pending_confirmation", "pending_fee"]

    def test_shows_pending_confirmation(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal_pending()

        _payload, response = withdraw(client_key, account_key)

        status, response = RequestGenerator.GET_withdrawal(client_key, response["withdrawal_key"])
        assert status == 200
        assert response["status"] == "pending_confirmation"
        assert values_of(response["status_events"], "status") == ["pending_confirmation"]

    def test_shows_reversed(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal_refused()

        _payload, response = withdraw(client_key, account_key)

        status, response = RequestGenerator.GET_withdrawal(client_key, response["withdrawal_key"])
        assert status == 200
        assert response["status"] == "reversed"
        assert values_of(response["status_events"], "status") == ["pending_confirmation", "reversed"]

    def test_refuses_unknown_withdrawal_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        status, response = RequestGenerator.GET_withdrawal(client_key, str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001017"

    def test_refuses_withdrawal_of_another_client(self):
        Mock().clear()
        owner_client_key, account_key = open_account_with_balance("100.00")
        other_client_key = ObjectGenerator.configure_client()
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(owner_client_key)

        _payload, response = withdraw(owner_client_key, account_key)
        withdrawal_key = response["withdrawal_key"]

        status, _response = RequestGenerator.GET_withdrawal(owner_client_key, withdrawal_key)
        assert status == 200

        status, response = RequestGenerator.GET_withdrawal(other_client_key, withdrawal_key)
        assert status == 404
        assert response["code"] == "QIT001017"
