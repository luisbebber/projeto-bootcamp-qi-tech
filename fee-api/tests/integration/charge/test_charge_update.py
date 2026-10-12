from uuid import uuid4

from tests.utils import ObjectGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestChargeUpdate:

    def test_marks_charge_as_paid(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()
        charge_key = charge["charge_key"]

        status, response = RequestGenerator.PATCH_charge(client_key, charge_key, {"status": "paid"})
        assert status == 200
        assert response == {"charge_key": charge_key, "status": "paid"}

        _status, charge_get = RequestGenerator.GET_charge(client_key, charge_key)
        assert charge_get["status"] == "paid"

        _status, paid_listing = RequestGenerator.GET_charges(client_key, {"status": "paid"})
        assert paid_listing["data"][0]["charge_key"] == charge_key
        _status, pending_listing = RequestGenerator.GET_charges(client_key, {"status": "pending_payment"})
        assert pending_listing["data"] == []

    def test_refuses_charge_that_is_not_pending(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()
        charge_key = charge["charge_key"]
        RequestGenerator.PATCH_charge(client_key, charge_key, {"status": "paid"})

        status, response = RequestGenerator.PATCH_charge(client_key, charge_key, {"status": "paid"})
        assert status == 409
        assert response["code"] == "QIT001011"

        _status, listing = RequestGenerator.GET_charges(client_key, {"status": "paid"})
        assert listing["data"][0]["status"] == "paid"

    def test_refuses_unknown_charge(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.PATCH_charge(client_key, str(uuid4()), {"status": "paid"})
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_refuses_charge_of_another_client(self):
        Mock().clear()
        owner_client_key, charge = ObjectGenerator.close_last_month()
        other_client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.PATCH_charge(other_client_key, charge["charge_key"], {"status": "paid"})
        assert status == 404
        assert response["code"] == "QIT001010"

        _status, listing = RequestGenerator.GET_charges(owner_client_key, {"status": "pending_payment"})
        assert listing["data"][0]["charge_key"] == charge["charge_key"]

    def test_refuses_malformed_body(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()

        broken_payloads = {
            "missing status": {},
            "status pending_payment": {"status": "pending_payment"},
            "unknown status": {"status": "refunded"},
            "extra field": {"status": "paid", "amount": "1.00"},
        }

        for name, broken_payload in broken_payloads.items():
            status, response = RequestGenerator.PATCH_charge(client_key, charge["charge_key"], broken_payload)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"
