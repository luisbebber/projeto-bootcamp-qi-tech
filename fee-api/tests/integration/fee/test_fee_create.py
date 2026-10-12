from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestFeeCreate:

    def test_records_fee(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)

        for fee_type, expected_amount in [("transfer", "0.50"), ("account_opening", "2.00")]:
            fee_payload = PayloadGenerator.create_fee_payload(fee_type=fee_type)

            status, response = RequestGenerator.POST_fee(client_key, fee_payload)
            assert status == 201
            fee_key = response["fee_key"]
            assert response == {"fee_key": fee_key}

            get_status, get_response = RequestGenerator.GET_fee(client_key, fee_key)
            assert get_status == 200
            assert get_response.pop("created_at") is not None
            assert get_response == {
                "fee_key": fee_key,
                "client_key": client_key,
                "fee_type": fee_type,
                "amount": expected_amount,
                "idempotency_key": fee_payload["idempotency_key"],
                "charge_key": None,
            }

    def test_does_not_call_client_api(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        Mock().clear()
        status, _response = RequestGenerator.POST_fee(client_key, PayloadGenerator.create_fee_payload())
        assert status == 201

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_repeated_key_returns_stored_response(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        idempotency_key = str(uuid4())

        first_payload = PayloadGenerator.create_fee_payload(fee_type="transfer", idempotency_key=idempotency_key)
        first_status, first_response = RequestGenerator.POST_fee(client_key, first_payload)
        assert first_status == 201

        second_payload = PayloadGenerator.create_fee_payload(fee_type="account_opening", idempotency_key=idempotency_key)
        second_status, second_response = RequestGenerator.POST_fee(client_key, second_payload)
        assert second_status == 201
        assert second_response == first_response

        _status, fee = RequestGenerator.GET_fee(client_key, first_response["fee_key"])
        assert fee["fee_type"] == "transfer"
        assert fee["amount"] == "0.50"

    def test_refuses_client_without_fees(self):
        Mock().clear()
        client_key = str(uuid4())
        fee_payload = PayloadGenerator.create_fee_payload()

        status, response = RequestGenerator.POST_fee(client_key, fee_payload)
        assert status == 404
        assert response["code"] == "QIT001005"

        ObjectGenerator.register_fee_configuration(client_key=client_key)

        status, response = RequestGenerator.POST_fee(client_key, fee_payload)
        assert status == 201

        _status, fee = RequestGenerator.GET_fee(client_key, response["fee_key"])
        assert fee["idempotency_key"] == fee_payload["idempotency_key"]

    def test_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        valid_payload = PayloadGenerator.create_fee_payload()

        broken_payloads = {
            "missing idempotency_key": {"fee_type": "transfer"},
            "missing fee_type": {"idempotency_key": str(uuid4())},
            "unknown fee_type": {**valid_payload, "fee_type": "pix"},
            "idempotency_key is not a UUID": {**valid_payload, "idempotency_key": "abc"},
            "extra field": {**valid_payload, "amount": "1.00"},
        }

        for name, broken_payload in broken_payloads.items():
            status, response = RequestGenerator.POST_fee(client_key, broken_payload)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"

    def test_records_the_value_in_force_at_that_moment(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)
        old_fee_key = ObjectGenerator.record_fee(client_key, fee_type="transfer")["fee_key"]

        status, _response = RequestGenerator.PATCH_fee_configuration(client_key, {"transfer_amount": "1.25"})
        assert status == 200
        new_fee_key = ObjectGenerator.record_fee(client_key, fee_type="transfer")["fee_key"]

        _status, old_fee = RequestGenerator.GET_fee(client_key, old_fee_key)
        _status, new_fee = RequestGenerator.GET_fee(client_key, new_fee_key)
        assert old_fee["amount"] == "0.50"
        assert new_fee["amount"] == "1.25"
