from decimal import Decimal
from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import rows_of, sum_of_amounts, values_of
from tests.utils.mock_generator import FeeApiMock, SpiApiMock
from tests.utils.mock_utils import Mock


def open_account_with_movements() -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]
    other_account_key = ObjectGenerator.create_account(client_key)["account_key"]

    ObjectGenerator.create_deposit(client_key, account_key, amount="100.00")
    ObjectGenerator.create_withdrawal(client_key, account_key, amount="30.00")
    ObjectGenerator.create_deposit(client_key, other_account_key, amount="10.00")
    ObjectGenerator.create_transfer(client_key, account_key, other_account_key, amount="20.00")
    ObjectGenerator.create_transfer(client_key, other_account_key, account_key, amount="5.00")

    return client_key, account_key


class TestStatementGet:

    def test_lists_statement_newest_first(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        status, response = RequestGenerator.GET_statement(client_key, account_key)
        assert status == 200
        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True

        created_ats = values_of(response["data"], "created_at")
        assert response["data"] == [
            {"type": "transfer_in", "amount": "5.00", "balance_after": "55.00", "created_at": created_ats[0]},
            {"type": "transfer_out", "amount": "-20.00", "balance_after": "50.00", "created_at": created_ats[1]},
            {"type": "withdrawal", "amount": "-30.00", "balance_after": "70.00", "created_at": created_ats[2]},
            {"type": "deposit", "amount": "100.00", "balance_after": "100.00", "created_at": created_ats[3]},
        ]

    def test_shows_withdrawal_reversal(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.create_deposit(client_key, account_key, amount="100.00")

        SpiApiMock.POST_withdrawal_refused()
        FeeApiMock.POST_fee(client_key)
        payload = PayloadGenerator.create_withdrawal_payload(amount="40.00")
        RequestGenerator.POST_withdrawal(client_key, account_key, payload)

        status, response = RequestGenerator.GET_statement(client_key, account_key)
        assert status == 200
        assert rows_of(response["data"], "type", "amount", "balance_after") == [
            ("withdrawal_reversed", "40.00", "100.00"),
            ("withdrawal", "-40.00", "60.00"),
            ("deposit", "100.00", "100.00"),
        ]

    def test_statement_adds_up_to_balance(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        _status, statement = RequestGenerator.GET_statement(client_key, account_key, {"limit": "100"})
        entries = statement["data"]

        _status, account = RequestGenerator.GET_account(client_key, account_key)
        assert sum_of_amounts(entries) == Decimal(account["balance"])
        assert entries[0]["balance_after"] == account["balance"]

        for newer, older in zip(entries, entries[1:]):
            assert Decimal(newer["balance_after"]) == Decimal(older["balance_after"]) + Decimal(newer["amount"])

    def test_paginates_without_repeating_or_skipping(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        _status, full_statement = RequestGenerator.GET_statement(client_key, account_key)

        status, first_page = RequestGenerator.GET_statement(client_key, account_key, {"limit": "2", "page": "0"})
        assert status == 200
        assert len(first_page["data"]) == 2
        assert first_page["is_last_page"] is False

        status, second_page = RequestGenerator.GET_statement(client_key, account_key, {"limit": "2", "page": "1"})
        assert status == 200
        assert len(second_page["data"]) == 2
        assert second_page["is_last_page"] is True

        assert first_page["data"] + second_page["data"] == full_statement["data"]

    def test_filters_by_period_with_both_ends_included(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        _status, full_statement = RequestGenerator.GET_statement(client_key, account_key)
        newest, second, third, oldest = full_statement["data"]

        _status, response = RequestGenerator.GET_statement(client_key, account_key, {"_from": third["created_at"]})
        assert response["data"] == [newest, second, third]

        _status, response = RequestGenerator.GET_statement(client_key, account_key, {"_to": second["created_at"]})
        assert response["data"] == [second, third, oldest]

        params = {"_from": third["created_at"], "_to": second["created_at"]}
        _status, response = RequestGenerator.GET_statement(client_key, account_key, params)
        assert response["data"] == [second, third]

        _status, response = RequestGenerator.GET_statement(client_key, account_key, {"_from": "2999-01-01T00:00:00"})
        assert response["data"] == []

    def test_lists_nothing_for_account_without_movements(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        status, response = RequestGenerator.GET_statement(client_key, account_key)
        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        status, response = RequestGenerator.GET_statement(client_key, str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        owner_client_key, account_key = open_account_with_movements()
        other_client_key = ObjectGenerator.configure_client()

        status, _response = RequestGenerator.GET_statement(owner_client_key, account_key)
        assert status == 200

        status, response = RequestGenerator.GET_statement(other_client_key, account_key)
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_schema_refuses_malformed_query_params(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        crooked_params = [
            {"parametro_que_nao_existe": "1"},
            {"limit": "0"},
            {"limit": "101"},
            {"limit": "abc"},
            {"page": "-1"},
            {"_from": "2026-10-12"},
            {"_from": "12/10/2026 14:30"},
            {"_to": "2026-10-12 14:30:00"},
            {"_to": "2026-10-12T14:30:00Z"},
        ]
        for params in crooked_params:
            status, response = RequestGenerator.GET_statement(client_key, account_key, params)

            assert status == 400, f"os parâmetros {params} foram aceitos"
            assert response["code"] == "QIT000001"

    def test_refuses_impossible_date_and_inverted_period(self):
        Mock().clear()
        client_key, account_key = open_account_with_movements()

        impossible_date = {"_from": "2026-02-30T10:00:00"}
        inverted_period = {"_from": "2026-10-12T10:00:00", "_to": "2026-10-11T10:00:00"}
        for params in [impossible_date, inverted_period]:
            status, response = RequestGenerator.GET_statement(client_key, account_key, params)

            assert status == 400, f"os parâmetros {params} foram aceitos"
            assert response["code"] == "QIT000010"
