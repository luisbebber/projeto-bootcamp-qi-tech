from uuid import uuid4

from tests.utils import DbUtils, ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock
from tests.utils.month_utils import month_label


class TestChargeCreate:

    def test_closes_the_month(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)
        fee_keys = []
        fee_types = ["transfer", "transfer", "account_opening"]
        for fee_type in fee_types:
            fee_keys.append(ObjectGenerator.record_fee(client_key, fee_type=fee_type)["fee_key"])
        DbUtils.move_client_dates_back(client_key, 1)

        charge_payload = PayloadGenerator.create_charge_payload(month_label(1))
        status, response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 201
        charge_key = response["charge_key"]
        assert response == {
            "charge_key": charge_key,
            "month": month_label(1),
            "amount": "3.00",
            "status": "pending_payment",
        }

        _status, charge_get = RequestGenerator.GET_charge(client_key, charge_key)
        assert charge_get["amount"] == "3.00"
        assert charge_get["status"] == "pending_payment"

        for fee_key in fee_keys:
            _status, fee = RequestGenerator.GET_fee(client_key, fee_key)
            assert fee["charge_key"] == charge_key

    def test_leaves_out_fees_of_other_months_and_other_clients(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        other_client_key = ObjectGenerator.register_fee_configuration()
        ObjectGenerator.record_fee(client_key, fee_type="transfer")
        other_fee_key = ObjectGenerator.record_fee(other_client_key, fee_type="transfer")["fee_key"]
        DbUtils.move_client_dates_back(client_key, 1)
        DbUtils.move_client_dates_back(other_client_key, 1)
        open_month_fee_key = ObjectGenerator.record_fee(client_key, fee_type="account_opening")["fee_key"]

        charge_payload = PayloadGenerator.create_charge_payload(month_label(1))
        status, response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 201
        assert response["amount"] == "0.50"

        _status, open_month_fee = RequestGenerator.GET_fee(client_key, open_month_fee_key)
        assert open_month_fee["charge_key"] is None
        _status, other_fee = RequestGenerator.GET_fee(other_client_key, other_fee_key)
        assert other_fee["charge_key"] is None

    def test_closes_month_without_fees_as_zero_charge(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        DbUtils.move_client_dates_back(client_key, 2)

        charge_payload = PayloadGenerator.create_charge_payload(month_label(1))
        status, response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 201
        assert response["amount"] == "0.00"
        assert response["status"] == "pending_payment"

    def test_refuses_month_already_closed(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()

        charge_payload = PayloadGenerator.create_charge_payload(month_label(1))
        status, response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 409
        assert response["code"] == "QIT001012"

        _status, charge_get = RequestGenerator.GET_charge(client_key, charge["charge_key"])
        assert charge_get["amount"] == "0.50"
        _status, listing = RequestGenerator.GET_charges(client_key)
        assert len(listing["data"]) == 1

    def test_refuses_month_that_has_not_ended(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        fee_key = ObjectGenerator.record_fee(client_key)["fee_key"]

        for months_ago in [0, -1]:
            charge_payload = PayloadGenerator.create_charge_payload(month_label(months_ago))
            status, response = RequestGenerator.POST_charge(client_key, charge_payload)
            assert status == 422, f"{months_ago} answered {status}"
            assert response["code"] == "QIT001008"

        _status, fee = RequestGenerator.GET_fee(client_key, fee_key)
        assert fee["charge_key"] is None
        _status, listing = RequestGenerator.GET_charges(client_key)
        assert listing["data"] == []

    def test_refuses_month_before_the_registration(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        DbUtils.move_client_dates_back(client_key, 1)

        charge_payload = PayloadGenerator.create_charge_payload(month_label(2))
        status, response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 422
        assert response["code"] == "QIT001009"

        charge_payload = PayloadGenerator.create_charge_payload(month_label(1))
        status, _response = RequestGenerator.POST_charge(client_key, charge_payload)
        assert status == 201

    def test_refuses_client_without_fees(self):
        Mock().clear()

        status, response = RequestGenerator.POST_charge(str(uuid4()), PayloadGenerator.create_charge_payload(month_label(1)))
        assert status == 404
        assert response["code"] == "QIT001005"

    def test_does_not_call_client_api(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        DbUtils.move_client_dates_back(client_key, 1)

        Mock().clear()
        status, _response = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(1)))
        assert status == 201

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        broken_payloads = {
            "missing month": {},
            "month 13": {"month": "2026-13"},
            "month without zero": {"month": "2026-1"},
            "month with day": {"month": "2026-09-01"},
            "extra field": {"month": month_label(1), "amount": "1.00"},
            "month as number": {"month": 202609},
        }

        for name, broken_payload in broken_payloads.items():
            status, response = RequestGenerator.POST_charge(client_key, broken_payload)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"
