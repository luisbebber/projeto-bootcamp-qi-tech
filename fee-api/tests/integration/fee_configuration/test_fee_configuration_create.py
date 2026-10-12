from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_generator import ClientApiMock
from tests.utils.mock_utils import Mock


class TestFeeConfigurationCreate:

    def test_registers_fees(self):
        Mock().clear()
        client_key = str(uuid4())
        ClientApiMock.GET_client(client_key)

        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 201
        assert response == {
            "client_key": client_key,
            "fees": [
                {"fee_type": "transfer", "amount": "0.50", "status": "active"},
                {"fee_type": "account_opening", "amount": "2.00", "status": "active"},
            ],
        }

        received_requests = Mock().retrieve_requests("GET", f"/client-api/client/{client_key}")
        assert len(received_requests) == 1
        sent_token = received_requests[0]["headers"]["INTERNAL-TOKEN"]
        assert len(sent_token) == 1
        assert sent_token[0] != ""

        get_status, get_response = RequestGenerator.GET_fee_configuration(client_key)
        assert get_status == 200
        assert get_response == response

        status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 409

    def test_accepts_zero_and_normalizes_amounts(self):
        Mock().clear()
        client_key = str(uuid4())
        ClientApiMock.GET_client(client_key)

        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0", account_opening_amount="05.5")
        status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 201
        assert response["fees"] == [
            {"fee_type": "transfer", "amount": "0.00", "status": "active"},
            {"fee_type": "account_opening", "amount": "5.50", "status": "active"},
        ]

        get_status, get_response = RequestGenerator.GET_fee_configuration(client_key)
        assert get_status == 200
        assert get_response == response

    def test_refuses_already_configured_client(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        Mock().clear()
        ClientApiMock.GET_client(client_key)

        other_payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="9.99", account_opening_amount="9.99")
        status, response = RequestGenerator.POST_fee_configuration(client_key, other_payload)
        assert status == 409
        assert response["code"] == "QIT001001"

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_client_not_found_in_client_api(self):
        Mock().clear()
        client_key = str(uuid4())
        ClientApiMock.GET_client_not_found(client_key)

        payload = PayloadGenerator.create_fee_configuration_payload()
        status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 404
        assert response["code"] == "QIT001002"

        Mock().clear()
        ClientApiMock.GET_client(client_key)

        status, _response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 201

    def test_refuses_inactive_client(self):
        Mock().clear()
        client_key = str(uuid4())
        ClientApiMock.GET_client(client_key, status="inactivated")

        payload = PayloadGenerator.create_fee_configuration_payload()
        status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 409
        assert response["code"] == "QIT001003"

        Mock().clear()
        ClientApiMock.GET_client(client_key)

        status, _response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 201

    def test_client_api_failure(self):
        failures = [
            ClientApiMock.GET_client_server_error,
            ClientApiMock.GET_client_connection_dropped,
        ]

        for teach_failure in failures:
            Mock().clear()
            client_key = str(uuid4())
            teach_failure(client_key)

            payload = PayloadGenerator.create_fee_configuration_payload()
            status, response = RequestGenerator.POST_fee_configuration(client_key, payload)
            assert status == 502, f"{teach_failure.__name__} answered {status}"
            assert response["code"] == "QIT001004"

            Mock().clear()
            ClientApiMock.GET_client(client_key)

            status, _response = RequestGenerator.POST_fee_configuration(client_key, payload)
            assert status == 201

    def test_refuses_malformed_body(self):
        valid_payload = PayloadGenerator.create_fee_configuration_payload()

        broken_payloads = {
            "missing account_opening_amount": {"transfer_amount": "0.50"},
            "missing transfer_amount": {"account_opening_amount": "2.00"},
            "extra field": {**valid_payload, "other_amount": "1.00"},
            "money as number": {**valid_payload, "transfer_amount": 0.5},
            "negative": {**valid_payload, "transfer_amount": "-1.00"},
            "three decimal places": {**valid_payload, "transfer_amount": "1.001"},
            "fourteen integer digits": {**valid_payload, "account_opening_amount": "12345678901234"},
            "not a number": {**valid_payload, "account_opening_amount": "abc"},
        }

        for name, broken_payload in broken_payloads.items():
            Mock().clear()
            client_key = str(uuid4())
            ClientApiMock.GET_client(client_key)

            status, response = RequestGenerator.POST_fee_configuration(client_key, broken_payload)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"

            assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []
