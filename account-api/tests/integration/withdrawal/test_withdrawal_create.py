from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import get_balance, spi_withdrawal_requests, transfer_fee_requests
from tests.utils.mock_generator import FeeApiMock, SpiApiMock
from tests.utils.mock_utils import Mock


def open_account_with_balance(amount: str) -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]
    ObjectGenerator.create_deposit(client_key, account_key, amount=amount)

    return client_key, account_key


class TestWithdrawalCreate:

    def test_withdraws(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_withdrawal_payload(amount="30")
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 201

        withdrawal_key = response["withdrawal_key"]
        assert response == {"withdrawal_key": withdrawal_key, "status": "completed"}
        assert get_balance(client_key, account_key) == "70.00"

        spi_requests = spi_withdrawal_requests()
        assert len(spi_requests) == 1
        assert spi_requests[0]["body"]["json"] == {
            "idempotency_key": withdrawal_key,
            "amount": "30.00",
            "receiver_data": payload["receiver_data"],
        }

        fee_requests = transfer_fee_requests(client_key)
        assert len(fee_requests) == 2
        assert fee_requests[1]["body"]["json"] == {
            "fee_type": "transfer",
            "idempotency_key": payload["idempotency_key"],
        }

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()

        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, {})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_withdrawal_payload()
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        crooked_fields = [
            ("amount", "-1"),
            ("amount", "1.234"),
            ("amount", "abc"),
            ("amount", 10),
            ("idempotency_key", "isto-nao-e-um-uuid"),
            ("receiver_data", {}),
            ("receiver_data", "texto"),
        ]
        for field, crooked_value in crooked_fields:
            payload = PayloadGenerator.create_withdrawal_payload()
            payload[field] = crooked_value

            status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)

            assert status == 400, f"o campo '{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

        crooked_receiver_fields = [
            ("ispb", "123"),
            ("account_type", "ouro"),
            ("owner_document_number", "1234567890"),
            ("account_digit", "12"),
        ]
        for field, crooked_value in crooked_receiver_fields:
            payload = PayloadGenerator.create_withdrawal_payload()
            payload["receiver_data"][field] = crooked_value

            status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)

            assert status == 400, f"o campo 'receiver_data.{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_withdrawal_payload()
        del payload["receiver_data"]["owner_name"]
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_withdrawal_payload()
        payload["receiver_data"]["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        assert get_balance(client_key, account_key) == "100.00"
        assert spi_withdrawal_requests() == []

    def test_refuses_zero_amount(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()

        for zero_amount in ["0", "0.00"]:
            payload = PayloadGenerator.create_withdrawal_payload(amount=zero_amount)
            status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)

            assert status == 422, f"o valor '{zero_amount}' foi aceito"
            assert response["code"] == "QIT001012"

        assert get_balance(client_key, account_key) == "100.00"
        assert spi_withdrawal_requests() == []

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        SpiApiMock.POST_withdrawal()

        payload = PayloadGenerator.create_withdrawal_payload()
        status, response = RequestGenerator.POST_withdrawal(client_key, str(uuid4()), payload)
        assert status == 404
        assert response["code"] == "QIT001010"

        assert spi_withdrawal_requests() == []

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        owner_client_key, account_key = open_account_with_balance("100.00")
        other_client_key = ObjectGenerator.configure_client()
        SpiApiMock.POST_withdrawal()

        payload = PayloadGenerator.create_withdrawal_payload()
        status, response = RequestGenerator.POST_withdrawal(other_client_key, account_key, payload)
        assert status == 404
        assert response["code"] == "QIT001010"

        assert get_balance(owner_client_key, account_key) == "100.00"
        assert spi_withdrawal_requests() == []

    def test_refuses_closed_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.close_account(client_key, account_key)
        SpiApiMock.POST_withdrawal()

        payload = PayloadGenerator.create_withdrawal_payload()
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 409
        assert response["code"] == "QIT001013"

        assert spi_withdrawal_requests() == []

    def test_refuses_insufficient_balance(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("10.00")
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_withdrawal_payload(amount="10.01")
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 422
        assert response["code"] == "QIT001015"
        assert get_balance(client_key, account_key) == "10.00"
        assert spi_withdrawal_requests() == []

        payload = PayloadGenerator.create_withdrawal_payload(amount="10.00")
        status, _response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 201
        assert get_balance(client_key, account_key) == "0.00"

    def test_retry_with_same_idempotency_key_returns_original_response(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_withdrawal_payload(amount="40.00")
        first_status, first_response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert first_status == 201

        second_status, second_response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert second_status == 201
        assert second_response == first_response

        assert get_balance(client_key, account_key) == "60.00"
        assert len(spi_withdrawal_requests()) == 1
        assert len(transfer_fee_requests(client_key)) == 2

    def test_spi_refusal_reverses_withdrawal(self):
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")
        SpiApiMock.POST_withdrawal_refused()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_withdrawal_payload(amount="40.00")
        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 201
        assert response == {"withdrawal_key": response["withdrawal_key"], "status": "reversed"}

        assert get_balance(client_key, account_key) == "100.00"
        assert len(transfer_fee_requests(client_key)) == 1

        status, retry_response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 201
        assert retry_response == response
        assert len(spi_withdrawal_requests()) == 1

    def test_spi_without_confirmation_keeps_withdrawal_pending(self):
        for teach_failure in [
            SpiApiMock.POST_withdrawal_pending,
            SpiApiMock.POST_withdrawal_server_error,
            SpiApiMock.POST_withdrawal_connection_dropped,
        ]:
            Mock().clear()
            client_key, account_key = open_account_with_balance("100.00")
            FeeApiMock.POST_fee(client_key)
            teach_failure()

            payload = PayloadGenerator.create_withdrawal_payload(amount="25.00")
            status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
            assert status == 202, f"{teach_failure.__name__} answered {status}"
            assert response == {"withdrawal_key": response["withdrawal_key"], "status": "pending_confirmation"}

            assert get_balance(client_key, account_key) == "75.00"
            assert len(transfer_fee_requests(client_key)) == 1

            status, retry_response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
            assert status == 202
            assert retry_response == response
            assert len(spi_withdrawal_requests()) == 1

    def test_fee_api_failure_still_completes_withdrawal(self):
        for teach_failure in [FeeApiMock.POST_fee_not_found, FeeApiMock.POST_fee_connection_dropped]:
            Mock().clear()
            client_key, account_key = open_account_with_balance("100.00")

            Mock().clear()
            SpiApiMock.POST_withdrawal()
            teach_failure(client_key)

            payload = PayloadGenerator.create_withdrawal_payload(amount="25.00")
            status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
            assert status == 201, f"{teach_failure.__name__} answered {status}"
            assert response == {"withdrawal_key": response["withdrawal_key"], "status": "completed"}
            assert get_balance(client_key, account_key) == "75.00"

            status, retry_response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
            assert status == 201
            assert retry_response == response
            assert len(spi_withdrawal_requests()) == 1
            assert len(transfer_fee_requests(client_key)) == 1
