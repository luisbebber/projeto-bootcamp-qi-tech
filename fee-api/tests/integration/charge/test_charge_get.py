from uuid import uuid4

from tests.utils import ObjectGenerator, RequestGenerator
from tests.utils.mock_utils import Mock
from tests.utils.month_utils import month_label


class TestChargeGet:

    def test_gets_charge(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()

        status, response = RequestGenerator.GET_charge(client_key, charge["charge_key"])
        assert status == 200
        assert response.pop("created_at") is not None
        assert response == {
            "charge_key": charge["charge_key"],
            "client_key": client_key,
            "month": month_label(1),
            "amount": "0.50",
            "status": "pending_payment",
        }

    def test_refuses_unknown_charge(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.GET_charge(client_key, str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_refuses_charge_of_another_client(self):
        Mock().clear()
        _owner_client_key, charge = ObjectGenerator.close_last_month()
        other_client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.GET_charge(other_client_key, charge["charge_key"])
        assert status == 404
        assert response["code"] == "QIT001010"
