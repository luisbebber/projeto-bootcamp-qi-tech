from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import get_balance, rows_of, spi_withdrawal_requests, transfer_fee_requests, values_of
from tests.utils.mock_generator import FeeApiMock
from tests.utils.mock_utils import Mock


def open_account_with_balance(amount: str) -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]
    ObjectGenerator.create_deposit(client_key, account_key, amount=amount)

    return client_key, account_key


def get_withdrawal_status(client_key: str, withdrawal_key: str) -> tuple:
    _status, response = RequestGenerator.GET_withdrawal(client_key, withdrawal_key)

    return response["status"], values_of(response["status_events"], "status")


def resolve(client_key: str, withdrawal_key: str, new_status: str) -> tuple:
    payload = PayloadGenerator.create_withdrawal_status_payload(new_status)

    return RequestGenerator.PATCH_withdrawal(client_key, withdrawal_key, payload)


class TestWithdrawalUpdate:

    def test_confirms_withdrawal_pending_confirmation(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        withdrawal_key, idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            client_key, account_key, "pending_confirmation", amount="30.00"
        )

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        status, response = resolve(client_key, withdrawal_key, "completed")
        assert status == 200
        assert response == {"withdrawal_key": withdrawal_key, "status": "completed"}

        fee_requests = transfer_fee_requests(client_key)
        assert len(fee_requests) == 1
        assert fee_requests[0]["body"]["json"] == {"fee_type": "transfer", "idempotency_key": idempotency_key}

        assert get_withdrawal_status(client_key, withdrawal_key) == (
            "completed",
            ["pending_confirmation", "pending_fee", "completed"],
        )
        assert get_balance(client_key, account_key) == "70.00"

    def test_fee_failure_leaves_withdrawal_pending_fee_and_can_be_retried(self):
        for teach_failure in [FeeApiMock.POST_fee_not_found, FeeApiMock.POST_fee_connection_dropped]:
            Mock().clear()
            client_key, account_key = open_account_with_balance("100.00")
            withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
                client_key, account_key, "pending_confirmation"
            )

            Mock().clear()
            teach_failure(client_key)
            status, response = resolve(client_key, withdrawal_key, "completed")
            assert status == 502, f"{teach_failure.__name__} answered {status}"
            assert response["code"] == "QIT001006"
            assert get_withdrawal_status(client_key, withdrawal_key) == (
                "pending_fee",
                ["pending_confirmation", "pending_fee"],
            )

            Mock().clear()
            FeeApiMock.POST_fee(client_key)
            status, response = resolve(client_key, withdrawal_key, "completed")
            assert status == 200
            assert response == {"withdrawal_key": withdrawal_key, "status": "completed"}
            assert get_withdrawal_status(client_key, withdrawal_key) == (
                "completed",
                ["pending_confirmation", "pending_fee", "completed"],
            )

    def test_completes_withdrawal_pending_fee(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        withdrawal_key, idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            client_key, account_key, "pending_fee"
        )

        Mock().clear()
        FeeApiMock.POST_fee_connection_dropped(client_key)
        status, response = resolve(client_key, withdrawal_key, "completed")
        assert status == 502
        assert response["code"] == "QIT001006"
        assert get_withdrawal_status(client_key, withdrawal_key)[0] == "pending_fee"

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        status, _response = resolve(client_key, withdrawal_key, "completed")
        assert status == 200

        fee_requests = transfer_fee_requests(client_key)
        assert len(fee_requests) == 1
        assert fee_requests[0]["body"]["json"]["idempotency_key"] == idempotency_key
        assert get_withdrawal_status(client_key, withdrawal_key)[0] == "completed"

    def test_reverses_withdrawal_pending_confirmation(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            client_key, account_key, "pending_confirmation", amount="40.00"
        )
        assert get_balance(client_key, account_key) == "60.00"

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        status, response = resolve(client_key, withdrawal_key, "reversed")
        assert status == 200
        assert response == {"withdrawal_key": withdrawal_key, "status": "reversed"}

        assert get_balance(client_key, account_key) == "100.00"
        assert get_withdrawal_status(client_key, withdrawal_key) == ("reversed", ["pending_confirmation", "reversed"])
        assert transfer_fee_requests(client_key) == []
        assert spi_withdrawal_requests() == []

        _status, statement = RequestGenerator.GET_statement(client_key, account_key)
        assert rows_of(statement["data"][:2], "type", "amount") == [
            ("withdrawal_reversed", "40.00"),
            ("withdrawal", "-40.00"),
        ]

    def test_refuses_transitions_that_are_not_allowed(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")

        forbidden = [
            ("completed", "completed"),
            ("completed", "reversed"),
            ("reversed", "completed"),
            ("reversed", "reversed"),
            ("pending_fee", "reversed"),
        ]
        for current_status, new_status in forbidden:
            withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
                client_key, account_key, current_status, amount="5.00"
            )
            balance_before = get_balance(client_key, account_key)
            trail_before = get_withdrawal_status(client_key, withdrawal_key)

            Mock().clear()
            FeeApiMock.POST_fee(client_key)
            status, response = resolve(client_key, withdrawal_key, new_status)

            assert status == 409, f"{current_status} → {new_status} answered {status}"
            assert response["code"] == "QIT001021"
            assert get_withdrawal_status(client_key, withdrawal_key) == trail_before
            assert get_balance(client_key, account_key) == balance_before
            assert transfer_fee_requests(client_key) == []

    def test_refuses_unknown_withdrawal_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        status, response = resolve(client_key, str(uuid4()), "completed")
        assert status == 404
        assert response["code"] == "QIT001017"

    def test_refuses_withdrawal_of_another_client(self):
        Mock().clear()
        owner_client_key, account_key = open_account_with_balance("100.00")
        other_client_key = ObjectGenerator.configure_client()
        withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            owner_client_key, account_key, "pending_confirmation", amount="30.00"
        )

        status, response = resolve(other_client_key, withdrawal_key, "reversed")
        assert status == 404
        assert response["code"] == "QIT001017"

        assert get_withdrawal_status(owner_client_key, withdrawal_key)[0] == "pending_confirmation"
        assert get_balance(owner_client_key, account_key) == "70.00"

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            client_key, account_key, "pending_confirmation"
        )

        crooked_payloads = [
            {},
            {"status": "pending_fee"},
            {"status": "pending_confirmation"},
            {"status": "COMPLETED"},
            {"status": 1},
            {"status": "completed", "campo_que_nao_existe": 1},
        ]
        for payload in crooked_payloads:
            status, response = RequestGenerator.PATCH_withdrawal(client_key, withdrawal_key, payload)

            assert status == 400, f"o corpo {payload} foi aceito"
            assert response["code"] == "QIT000001"

        assert get_withdrawal_status(client_key, withdrawal_key)[0] == "pending_confirmation"

    def test_resolved_withdrawal_stops_blocking_account_close(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("50.00")
        withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
            client_key, account_key, "pending_confirmation", amount="50.00"
        )

        close_payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, account_key, close_payload)
        assert status == 409
        assert response["code"] == "QIT001016"

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        status, _response = resolve(client_key, withdrawal_key, "completed")
        assert status == 200

        status, response = RequestGenerator.PATCH_account(client_key, account_key, close_payload)
        assert status == 200
        assert response["status"] == "closed"
