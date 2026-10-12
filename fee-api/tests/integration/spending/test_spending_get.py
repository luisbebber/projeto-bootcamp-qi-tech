from datetime import datetime, timedelta, timezone
from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.mock_utils import Mock
from tests.utils.month_utils import month_label

BRASILIA = timezone(timedelta(hours=-3))
DAY = timedelta(days=1)


def today() -> datetime:
    return datetime.now(BRASILIA)


def date_param(day: datetime) -> str:
    return day.strftime("%Y-%m-%d")


class TestSpendingGet:

    def test_sums_the_fees_of_the_month_by_type(self):
        Mock().clear()
        payload = PayloadGenerator.create_fee_configuration_payload(transfer_amount="0.50", account_opening_amount="2.00")
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)
        ObjectGenerator.record_fee(client_key, fee_type="transfer")
        ObjectGenerator.record_fee(client_key, fee_type="transfer")
        ObjectGenerator.record_fee(client_key, fee_type="account_opening")

        query_params = {"_from": date_param(today() - DAY), "_to": date_param(today() + DAY)}
        status, response = RequestGenerator.GET_spending(client_key, query_params)
        assert status == 200
        assert response == {
            "client_key": client_key,
            "months": [
                {
                    "month": today().strftime("%Y-%m"),
                    "fees": [
                        {"fee_type": "transfer", "amount": "1.00"},
                        {"fee_type": "account_opening", "amount": "2.00"},
                    ],
                }
            ],
            "paid_amount": "0.00",
            "payable_amount": "3.00",
        }

    def test_includes_both_ends_of_the_period(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        ObjectGenerator.record_fee(client_key, fee_type="transfer")

        query_params = {"_from": date_param(today()), "_to": date_param(today())}
        status, response = RequestGenerator.GET_spending(client_key, query_params)
        assert status == 200
        assert response["payable_amount"] == "0.50"

    def test_leaves_out_the_days_outside_the_period(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        ObjectGenerator.record_fee(client_key, fee_type="transfer")

        past_params = {"_from": date_param(today() - 5 * DAY), "_to": date_param(today() - DAY)}
        future_params = {"_from": date_param(today() + DAY), "_to": date_param(today() + 5 * DAY)}

        periods = {"past": past_params, "future": future_params}

        for name, query_params in periods.items():
            status, response = RequestGenerator.GET_spending(client_key, query_params)
            assert status == 200, f"{name} answered {status}"
            assert response == {"client_key": client_key, "months": [], "paid_amount": "0.00", "payable_amount": "0.00"}

    def test_shows_only_the_fees_of_that_client(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        other_client_key = ObjectGenerator.register_fee_configuration()
        ObjectGenerator.record_fee(client_key, fee_type="transfer")
        ObjectGenerator.record_fee(other_client_key, fee_type="transfer")
        ObjectGenerator.record_fee(other_client_key, fee_type="account_opening")

        query_params = {"_from": date_param(today()), "_to": date_param(today())}
        _status, response = RequestGenerator.GET_spending(client_key, query_params)
        assert response["payable_amount"] == "0.50"

    def test_does_not_call_client_api(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        Mock().clear()
        query_params = {"_from": date_param(today()), "_to": date_param(today())}
        status, _response = RequestGenerator.GET_spending(client_key, query_params)
        assert status == 200

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []

    def test_refuses_client_without_fees(self):
        query_params = {"_from": date_param(today()), "_to": date_param(today())}

        status, response = RequestGenerator.GET_spending(str(uuid4()), query_params)
        assert status == 404
        assert response["code"] == "QIT001005"

    def test_refuses_malformed_query(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()
        day = date_param(today())

        broken_queries = {
            "missing _from": {"_to": day},
            "missing _to": {"_from": day},
            "unknown parameter": {"_from": day, "_to": day, "status": "paid"},
            "date with time": {"_from": f"{day}T10:00:00", "_to": day},
            "date out of format": {"_from": "12/10/2026", "_to": day},
        }

        for name, query_params in broken_queries.items():
            status, response = RequestGenerator.GET_spending(client_key, query_params)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000001"

    def test_refuses_invalid_period(self):
        Mock().clear()
        client_key = ObjectGenerator.register_fee_configuration()

        invalid_queries = {
            "date that does not exist": {"_from": "2026-02-30", "_to": "2026-03-10"},
            "from after to": {"_from": "2026-10-12", "_to": "2026-10-11"},
        }

        for name, query_params in invalid_queries.items():
            status, response = RequestGenerator.GET_spending(client_key, query_params)
            assert status == 400, f"{name} answered {status}"
            assert response["code"] == "QIT000010"

    def test_moves_the_fees_to_paid_when_the_charge_is_paid(self):
        Mock().clear()
        client_key, charge = ObjectGenerator.close_last_month(fee_types=["transfer", "account_opening"])
        ObjectGenerator.record_fee(client_key, fee_type="transfer")
        query_params = {"_from": f"{month_label(1)}-01", "_to": date_param(today())}

        _status, response = RequestGenerator.GET_spending(client_key, query_params)
        assert response["paid_amount"] == "0.00"
        assert response["payable_amount"] == "3.00"

        RequestGenerator.PATCH_charge(client_key, charge["charge_key"], {"status": "paid"})

        _status, response = RequestGenerator.GET_spending(client_key, query_params)
        assert response["paid_amount"] == "2.50"
        assert response["payable_amount"] == "0.50"

        months = []
        for month in response["months"]:
            months.append(month["month"])
        assert months == [month_label(1), month_label(0)]
