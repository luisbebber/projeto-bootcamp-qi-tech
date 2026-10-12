from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestFeeConfigurationGet:

    def test_gets_active_fees(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)

        status, response = RequestGenerator.GET_fee_configuration(client_key)
        assert status == 200
        assert response == {
            "client_key": client_key,
            "fees": [
                {"fee_type": "transfer", "amount": "0.50", "status": "active"},
                {"fee_type": "account_opening", "amount": "2.00", "status": "active"},
            ],
        }

    def test_does_not_call_client_api(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        Mock().clear()
        status, _response = RequestGenerator.GET_fee_configuration(client_key)
        assert status == 200

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_shows_only_the_fees_of_that_client(self):
        Mock().clear()
        first_payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="1.00", account_opening_amount="3.00")
        second_payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="7.00", account_opening_amount="9.00")
        first_client_key = ObjectGenerator.register_fee_configuration(payload=first_payload)
        second_client_key = ObjectGenerator.register_fee_configuration(payload=second_payload)

        _status, first_response = RequestGenerator.GET_fee_configuration(first_client_key)
        _status, second_response = RequestGenerator.GET_fee_configuration(second_client_key)

        first_amounts = []
        for fee in first_response["fees"]:
            first_amounts.append(fee["amount"])
        assert first_amounts == ["1.00", "3.00"]

        second_amounts = []
        for fee in second_response["fees"]:
            second_amounts.append(fee["amount"])
        assert second_amounts == ["7.00", "9.00"]

    def test_refuses_client_without_fees(self):
        client_key = str(uuid4())

        status, response = RequestGenerator.GET_fee_configuration(client_key)
        assert status == 404
        assert response["code"] == "QIT001005"
