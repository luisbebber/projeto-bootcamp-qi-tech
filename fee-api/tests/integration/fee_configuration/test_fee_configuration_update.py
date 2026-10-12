from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestFeeConfigurationUpdate:

    def test_changes_both_fees(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        payload = PayloadGenerator.update_fee_configuration_payload(transfer_amount="1.25", account_opening_amount="4.00")
        status, response = RequestGenerator.PATCH_fee_configuration(client_key, payload)
        assert status == 200

        expected_fees = {
            "client_key": client_key,
            "fees": [
                {"fee_type": "transfer", "amount": "1.25", "status": "active"},
                {"fee_type": "account_opening", "amount": "4.00", "status": "active"},
            ],
        }
        assert response == expected_fees

        _status, get_response = RequestGenerator.GET_fee_configuration(client_key)
        assert get_response == expected_fees

    def test_changes_only_the_fee_in_the_body(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)

        status, _response = RequestGenerator.PATCH_fee_configuration(client_key, {"account_opening_amount": "3.00"})
        assert status == 200

        _status, get_response = RequestGenerator.GET_fee_configuration(client_key)
        amounts = []
        for fee in get_response["fees"]:
            amounts.append(fee["amount"])
        assert amounts == ["0.50", "3.00"]

    def test_skips_the_value_equal_to_the_active_one(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)

        update_payload = PayloadGenerator.update_fee_configuration_payload(transfer_amount="0.5", account_opening_amount="3.00")
        status, response = RequestGenerator.PATCH_fee_configuration(client_key, update_payload)
        assert status == 200
        amounts = []
        for fee in response["fees"]:
            amounts.append(fee["amount"])
        assert amounts == ["0.50", "3.00"]

    def test_accepts_zero(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.PATCH_fee_configuration(client_key, {"transfer_amount": "0"})
        assert status == 200
        assert response["fees"][0] == {"fee_type": "transfer", "amount": "0.00", "status": "active"}

    def test_refuses_when_nothing_changes(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)
        _status, before = RequestGenerator.GET_fee_configuration(client_key)

        same_payload = PayloadGenerator.update_fee_configuration_payload(transfer_amount="0.5", account_opening_amount="2")
        status, response = RequestGenerator.PATCH_fee_configuration(client_key, same_payload)
        assert status == 409
        assert response["code"] == "QIT001007"

        _status, after = RequestGenerator.GET_fee_configuration(client_key)
        assert after == before

    def test_refuses_client_without_fees(self):
        Mock().clear()

        status, response = RequestGenerator.PATCH_fee_configuration(str(uuid4()), {"transfer_amount": "1.00"})
        assert status == 404
        assert response["code"] == "QIT001005"

    def test_does_not_call_client_api(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        Mock().clear()
        status, _response = RequestGenerator.PATCH_fee_configuration(client_key, {"transfer_amount": "1.00"})
        assert status == 200

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        _status, before = RequestGenerator.GET_fee_configuration(client_key)

        broken_payloads = {
            "empty body": {},
            "unknown field": {"transfer_amount": "1.00", "pix_amount": "1.00"},
            "negative amount": {"transfer_amount": "-1.00"},
            "three decimal places": {"transfer_amount": "1.005"},
            "amount as number": {"transfer_amount": 1.0},
        }

        for name, broken_payload in broken_payloads.items():
            status, response = RequestGenerator.PATCH_fee_configuration(client_key, broken_payload)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"

        _status, after = RequestGenerator.GET_fee_configuration(client_key)
        assert after == before
