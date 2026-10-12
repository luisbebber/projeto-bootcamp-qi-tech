from uuid import uuid4

from tests.utils import DbUtils, ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock
from tests.utils.month_utils import month_label


class TestChargeList:

    def test_lists_the_charges_of_the_client(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month()

        status, response = RequestGenerator.GET_charges(client_key)
        assert status == 200
        item = response["data"][0]
        assert item.pop("created_at") is not None
        assert item == {
            "charge_key": charge["charge_key"],
            "client_key": client_key,
            "month": month_label(1),
            "amount": "0.50",
            "status": "pending_payment",
        }
        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True

    def test_filters_by_status(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        DbUtils.move_client_dates_back(client_key, 2)
        paid_charge = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(2)))[1]
        pending_charge = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(1)))[1]
        RequestGenerator.PATCH_charge(client_key, paid_charge["charge_key"], {"status": "paid"})

        _status, paid_listing = RequestGenerator.GET_charges(client_key, {"status": "paid"})
        assert len(paid_listing["data"]) == 1
        assert paid_listing["data"][0]["charge_key"] == paid_charge["charge_key"]

        _status, pending_listing = RequestGenerator.GET_charges(client_key, {"status": "pending_payment"})
        assert len(pending_listing["data"]) == 1
        assert pending_listing["data"][0]["charge_key"] == pending_charge["charge_key"]

    def test_paginates_newest_first(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        DbUtils.move_client_dates_back(client_key, 2)
        old_charge = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(2)))[1]
        new_charge = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(1)))[1]

        _status, first_page = RequestGenerator.GET_charges(client_key, {"limit": "1", "page": "0"})
        assert first_page["data"][0]["charge_key"] == new_charge["charge_key"]
        assert first_page["is_last_page"] is False

        _status, second_page = RequestGenerator.GET_charges(client_key, {"limit": "1", "page": "1"})
        assert second_page["data"][0]["charge_key"] == old_charge["charge_key"]
        assert second_page["is_last_page"] is True

    def test_shows_only_the_charges_of_that_client(self):
        Mock().clear()
        _client_key, charge = ObjectGenerator.close_last_month()
        other_client_key = ObjectGenerator.register_fee_configuration()

        status, response = RequestGenerator.GET_charges(other_client_key)
        assert status == 200
        assert response["data"] == []
        assert charge["charge_key"] is not None

    def test_refuses_client_without_fees(self):
        status, response = RequestGenerator.GET_charges(str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001005"

    def test_refuses_malformed_query(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        broken_queries = {
            "unknown status": {"status": "refunded"},
            "unknown parameter": {"month": "2026-09"},
            "limit zero": {"limit": "0"},
            "limit above 100": {"limit": "101"},
        }

        for name, query_params in broken_queries.items():
            status, response = RequestGenerator.GET_charges(client_key, query_params)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"
