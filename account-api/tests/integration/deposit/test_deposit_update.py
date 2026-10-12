from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import transfer_fee_requests, values_of
from tests.utils.mock_generator import FeeApiMock
from tests.utils.mock_utils import Mock


def open_account() -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]

    return client_key, account_key


def create_pending_fee_deposit(client_key: str, account_key: str) -> tuple:
    FeeApiMock.POST_fee_not_found(client_key)

    payload = PayloadGenerator.create_deposit_payload()
    status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
    assert status == 201

    Mock().clear()

    return response["deposit_key"], payload["idempotency_key"]


def is_pending_fee(deposit_key: str) -> bool:
    _status, response = RequestGenerator.GET_deposits({"status": "pending_fee", "limit": "100"})

    return deposit_key in values_of(response["data"], "deposit_key")


class TestDepositUpdate:

    def test_completes_pending_fee_deposit(self):
        Mock().clear()
        client_key, account_key = open_account()
        deposit_key, idempotency_key = create_pending_fee_deposit(client_key, account_key)
        assert is_pending_fee(deposit_key)

        FeeApiMock.POST_fee(client_key)
        payload = PayloadGenerator.create_deposit_status_payload()
        status, response = RequestGenerator.PATCH_deposit(client_key, deposit_key, payload)
        assert status == 200
        assert response == {"deposit_key": deposit_key, "status": "completed"}

        fee_requests = transfer_fee_requests(client_key)
        assert len(fee_requests) == 1
        assert fee_requests[0]["body"]["json"] == {"fee_type": "transfer", "idempotency_key": idempotency_key}

        assert not is_pending_fee(deposit_key)

    def test_refuses_deposit_that_is_not_pending_fee(self):
        Mock().clear()
        client_key, account_key = open_account()
        deposit_key = ObjectGenerator.create_deposit(client_key, account_key)["deposit_key"]

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        payload = PayloadGenerator.create_deposit_status_payload()
        status, response = RequestGenerator.PATCH_deposit(client_key, deposit_key, payload)
        assert status == 409
        assert response["code"] == "QIT001020"

        assert transfer_fee_requests(client_key) == []

    def test_fee_api_failure_keeps_deposit_pending_fee(self):
        for teach_failure in [FeeApiMock.POST_fee_not_found, FeeApiMock.POST_fee_connection_dropped]:
            Mock().clear()
            client_key, account_key = open_account()
            deposit_key, _idempotency_key = create_pending_fee_deposit(client_key, account_key)

            teach_failure(client_key)
            payload = PayloadGenerator.create_deposit_status_payload()
            status, response = RequestGenerator.PATCH_deposit(client_key, deposit_key, payload)
            assert status == 502, f"{teach_failure.__name__} answered {status}"
            assert response["code"] == "QIT001006"

            assert is_pending_fee(deposit_key)

    def test_refuses_unknown_deposit_key(self):
        Mock().clear()
        client_key, _account_key = open_account()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_deposit_status_payload()
        status, response = RequestGenerator.PATCH_deposit(client_key, str(uuid4()), payload)
        assert status == 404
        assert response["code"] == "QIT001019"

        assert transfer_fee_requests(client_key) == []

    def test_refuses_deposit_of_another_client(self):
        Mock().clear()
        owner_client_key, account_key = open_account()
        other_client_key, _other_account_key = open_account()
        deposit_key, _idempotency_key = create_pending_fee_deposit(owner_client_key, account_key)

        FeeApiMock.POST_fee(other_client_key)
        payload = PayloadGenerator.create_deposit_status_payload()
        status, response = RequestGenerator.PATCH_deposit(other_client_key, deposit_key, payload)
        assert status == 404
        assert response["code"] == "QIT001019"

        assert transfer_fee_requests(other_client_key) == []
        assert is_pending_fee(deposit_key)

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key, account_key = open_account()
        deposit_key, _idempotency_key = create_pending_fee_deposit(client_key, account_key)

        crooked_payloads = [
            {},
            {"status": "pending_fee"},
            {"status": "COMPLETED"},
            {"status": 1},
            {"status": "completed", "campo_que_nao_existe": 1},
        ]
        for payload in crooked_payloads:
            status, response = RequestGenerator.PATCH_deposit(client_key, deposit_key, payload)

            assert status == 400, f"o corpo {payload} foi aceito"
            assert response["code"] == "QIT000001"

        assert is_pending_fee(deposit_key)
