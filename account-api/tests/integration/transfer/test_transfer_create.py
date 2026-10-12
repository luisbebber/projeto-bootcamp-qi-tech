from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import get_balance, spi_withdrawal_requests, transfer_fee_requests
from tests.utils.mock_utils import Mock


def open_accounts(origin_balance: str) -> tuple:
    client_key = ObjectGenerator.configure_client()
    origin_account_key = ObjectGenerator.create_account(client_key)["account_key"]
    destination_account_key = ObjectGenerator.create_account(client_key)["account_key"]
    ObjectGenerator.create_deposit(client_key, origin_account_key, amount=origin_balance)

    return client_key, origin_account_key, destination_account_key


class TestTransferCreate:

    def test_transfers(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount="30.5")
        status, response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 201
        assert response == {"transfer_key": response["transfer_key"]}

        assert get_balance(client_key, origin_account_key) == "69.50"
        assert get_balance(client_key, destination_account_key) == "30.50"

        assert len(transfer_fee_requests(client_key)) == 1
        assert spi_withdrawal_requests() == []

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")

        status, response = RequestGenerator.POST_transfer(client_key, {})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key)
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        crooked_fields = [
            ("amount", "-1"),
            ("amount", "1.234"),
            ("amount", "abc"),
            ("amount", 10),
            ("origin_account_key", "isto-nao-e-um-uuid"),
            ("destination_account_key", ""),
            ("idempotency_key", "isto-nao-e-um-uuid"),
        ]
        for field, crooked_value in crooked_fields:
            payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key)
            payload[field] = crooked_value

            status, response = RequestGenerator.POST_transfer(client_key, payload)

            assert status == 400, f"o campo '{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

        assert get_balance(client_key, origin_account_key) == "100.00"
        assert get_balance(client_key, destination_account_key) == "0.00"

    def test_refuses_zero_amount(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")

        for zero_amount in ["0", "0.00"]:
            payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount=zero_amount)
            status, response = RequestGenerator.POST_transfer(client_key, payload)

            assert status == 422, f"o valor '{zero_amount}' foi aceito"
            assert response["code"] == "QIT001012"

        assert get_balance(client_key, origin_account_key) == "100.00"

    def test_refuses_same_origin_and_destination(self):
        Mock().clear()
        client_key, origin_account_key, _destination_account_key = open_accounts("100.00")

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, origin_account_key)
        status, response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 422
        assert response["code"] == "QIT001018"

        assert get_balance(client_key, origin_account_key) == "100.00"

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")

        unknown_origin = PayloadGenerator.create_transfer_payload(str(uuid4()), destination_account_key)
        unknown_destination = PayloadGenerator.create_transfer_payload(origin_account_key, str(uuid4()))
        for payload in [unknown_origin, unknown_destination]:
            status, response = RequestGenerator.POST_transfer(client_key, payload)

            assert status == 404
            assert response["code"] == "QIT001010"

        assert get_balance(client_key, origin_account_key) == "100.00"

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")
        other_client_key = ObjectGenerator.configure_client()
        other_account_key = ObjectGenerator.create_account(other_client_key)["account_key"]

        foreign_destination = PayloadGenerator.create_transfer_payload(origin_account_key, other_account_key)
        status, response = RequestGenerator.POST_transfer(client_key, foreign_destination)
        assert status == 404
        assert response["code"] == "QIT001010"

        foreign_origin = PayloadGenerator.create_transfer_payload(other_account_key, destination_account_key)
        status, response = RequestGenerator.POST_transfer(client_key, foreign_origin)
        assert status == 404
        assert response["code"] == "QIT001010"

        assert get_balance(client_key, origin_account_key) == "100.00"
        assert get_balance(other_client_key, other_account_key) == "0.00"

    def test_refuses_closed_account(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")
        closed_account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.close_account(client_key, closed_account_key)

        closed_destination = PayloadGenerator.create_transfer_payload(origin_account_key, closed_account_key)
        status, response = RequestGenerator.POST_transfer(client_key, closed_destination)
        assert status == 409
        assert response["code"] == "QIT001013"

        closed_origin = PayloadGenerator.create_transfer_payload(closed_account_key, destination_account_key)
        status, response = RequestGenerator.POST_transfer(client_key, closed_origin)
        assert status == 409
        assert response["code"] == "QIT001013"

        assert get_balance(client_key, origin_account_key) == "100.00"
        assert get_balance(client_key, destination_account_key) == "0.00"

    def test_refuses_insufficient_balance(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("10.00")

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount="10.01")
        status, response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 422
        assert response["code"] == "QIT001015"
        assert get_balance(client_key, origin_account_key) == "10.00"
        assert get_balance(client_key, destination_account_key) == "0.00"

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount="10.00")
        status, _response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 201
        assert get_balance(client_key, origin_account_key) == "0.00"
        assert get_balance(client_key, destination_account_key) == "10.00"

    def test_retry_with_same_idempotency_key_returns_original_response(self):
        Mock().clear()
        client_key, origin_account_key, destination_account_key = open_accounts("100.00")

        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount="40.00")
        first_status, first_response = RequestGenerator.POST_transfer(client_key, payload)
        assert first_status == 201

        second_status, second_response = RequestGenerator.POST_transfer(client_key, payload)
        assert second_status == 201
        assert second_response == first_response

        assert get_balance(client_key, origin_account_key) == "60.00"
        assert get_balance(client_key, destination_account_key) == "40.00"
