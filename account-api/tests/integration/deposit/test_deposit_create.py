from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import get_balance, transfer_fee_requests
from tests.utils.mock_generator import FeeApiMock
from tests.utils.mock_utils import Mock


class TestDepositCreate:

    def test_deposits(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        payload = PayloadGenerator.create_deposit_payload(amount="126.97")
        status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert status == 201

        deposit_key = response["deposit_key"]
        assert response == {"deposit_key": deposit_key, "balance_after": "126.97"}
        assert get_balance(client_key, account_key) == "126.97"

        fee_requests = transfer_fee_requests(client_key)
        assert len(fee_requests) == 1
        assert fee_requests[0]["body"]["json"] == {
            "fee_type": "transfer",
            "idempotency_key": payload["idempotency_key"],
        }

    def test_balance_accumulates(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        first_response = ObjectGenerator.create_deposit(client_key, account_key, amount="100")
        assert first_response["balance_after"] == "100.00"

        second_response = ObjectGenerator.create_deposit(client_key, account_key, amount="50.5")
        assert second_response["balance_after"] == "150.50"

        assert get_balance(client_key, account_key) == "150.50"

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        status, response = RequestGenerator.POST_deposit(client_key, account_key, {})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_deposit_payload()
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        crooked_fields = [
            ("amount", "-1"),
            ("amount", "1.234"),
            ("amount", "abc"),
            ("amount", "1e5"),
            ("amount", ""),
            ("amount", 10),
            ("idempotency_key", "isto-nao-e-um-uuid"),
        ]
        for field, crooked_value in crooked_fields:
            payload = PayloadGenerator.create_deposit_payload()
            payload[field] = crooked_value

            status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)

            assert status == 400, f"o campo '{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

        assert get_balance(client_key, account_key) == "0.00"
        assert transfer_fee_requests(client_key) == []

    def test_refuses_zero_amount(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        for zero_amount in ["0", "0.00", "00.0"]:
            payload = PayloadGenerator.create_deposit_payload(amount=zero_amount)
            status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)

            assert status == 422, f"o valor '{zero_amount}' foi aceito"
            assert response["code"] == "QIT001012"

        assert get_balance(client_key, account_key) == "0.00"
        assert transfer_fee_requests(client_key) == []

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_deposit_payload()
        status, response = RequestGenerator.POST_deposit(client_key, str(uuid4()), payload)
        assert status == 404
        assert response["code"] == "QIT001010"

        assert transfer_fee_requests(client_key) == []

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        owner_client_key = ObjectGenerator.configure_client()
        other_client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(owner_client_key)["account_key"]
        FeeApiMock.POST_fee(other_client_key)

        payload = PayloadGenerator.create_deposit_payload()
        status, response = RequestGenerator.POST_deposit(other_client_key, account_key, payload)
        assert status == 404
        assert response["code"] == "QIT001010"

        assert get_balance(owner_client_key, account_key) == "0.00"
        assert transfer_fee_requests(other_client_key) == []

    def test_refuses_closed_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.close_account(client_key, account_key)

        payload = PayloadGenerator.create_deposit_payload()
        status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert status == 409
        assert response["code"] == "QIT001013"

        assert transfer_fee_requests(client_key) == []

    def test_retry_with_same_idempotency_key_returns_original_response(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        payload = PayloadGenerator.create_deposit_payload(amount="40.00")
        first_status, first_response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert first_status == 201

        second_status, second_response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert second_status == 201
        assert second_response == first_response

        assert get_balance(client_key, account_key) == "40.00"
        assert len(transfer_fee_requests(client_key)) == 1

    def test_fee_api_failure_still_credits_account(self):
        for teach_failure in [FeeApiMock.POST_fee_not_found, FeeApiMock.POST_fee_connection_dropped]:
            Mock().clear()
            client_key = ObjectGenerator.configure_client()
            account_key = ObjectGenerator.create_account(client_key)["account_key"]

            Mock().clear()
            teach_failure(client_key)

            payload = PayloadGenerator.create_deposit_payload(amount="25.50")
            status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
            assert status == 201, f"{teach_failure.__name__} answered {status}"
            assert response["balance_after"] == "25.50"
            assert get_balance(client_key, account_key) == "25.50"

            status, retry_response = RequestGenerator.POST_deposit(client_key, account_key, payload)
            assert status == 201
            assert retry_response == response
            assert len(transfer_fee_requests(client_key)) == 1
