from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestFeeGet:

    def test_gets_fee(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)
        idempotency_key = str(uuid4())
        fee_key = ObjectGenerator.record_fee(client_key, fee_type="account_opening", idempotency_key=idempotency_key)["fee_key"]

        status, response = RequestGenerator.GET_fee(client_key, fee_key)
        assert status == 200
        assert response.pop("created_at") is not None
        assert response == {
            "fee_key": fee_key,
            "client_key": client_key,
            "fee_type": "account_opening",
            "amount": "2.00",
            "idempotency_key": idempotency_key,
            "charge_key": None,
        }

    def test_refuses_unknown_fee(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.GET_fee(client_key, str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001006"

    def test_refuses_fee_of_another_client(self):
        Mock().clear()
        owner_client_key = ObjectGenerator.register_fee_configuration()
        other_client_key = ObjectGenerator.register_fee_configuration()
        fee_key = ObjectGenerator.record_fee(owner_client_key)["fee_key"]

        status, response = RequestGenerator.GET_fee(other_client_key, fee_key)
        assert status == 404
        assert response["code"] == "QIT001006"
