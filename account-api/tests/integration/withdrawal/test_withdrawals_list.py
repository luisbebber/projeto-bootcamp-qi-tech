from tests.utils import DbUtils, ObjectGenerator, RequestGenerator
from tests.utils.checks import values_of
from tests.utils.mock_utils import Mock


def open_account_with_balance(amount: str) -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]
    ObjectGenerator.create_deposit(client_key, account_key, amount=amount)

    return client_key, account_key


class TestWithdrawalsList:

    def test_lists_withdrawals_by_status(self):
        DbUtils.rollback()
        Mock().clear()
        client_key, account_key = open_account_with_balance("200.00")

        keys_by_status = {}
        for final_status, amount in [("completed", "10.00"), ("pending_confirmation", "20.00"), ("reversed", "30.00"), ("pending_fee", "40.00")]:
            keys_by_status[final_status], _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
                client_key, account_key, final_status, amount=amount
            )

        status, response = RequestGenerator.GET_withdrawals()
        assert status == 200
        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True

        assert values_of(response["data"], "status") == ["pending_fee", "reversed", "pending_confirmation", "completed"]

        pending_confirmation_item = response["data"][2]
        assert pending_confirmation_item == {
            "withdrawal_key": keys_by_status["pending_confirmation"],
            "client_key": client_key,
            "account_key": account_key,
            "amount": "20.00",
            "status": "pending_confirmation",
            "created_at": pending_confirmation_item["created_at"],
        }

        for item in response["data"]:
            status, filtered = RequestGenerator.GET_withdrawals({"status": item["status"]})
            assert status == 200
            assert filtered["data"] == [item]

    def test_lists_withdrawals_of_every_client(self):
        DbUtils.rollback()
        Mock().clear()
        first_client_key, first_account_key = open_account_with_balance("100.00")
        second_client_key, second_account_key = open_account_with_balance("100.00")

        first_key, _ = ObjectGenerator.create_withdrawal_with_status(first_client_key, first_account_key, "pending_confirmation")
        second_key, _ = ObjectGenerator.create_withdrawal_with_status(second_client_key, second_account_key, "pending_confirmation")

        status, response = RequestGenerator.GET_withdrawals({"status": "pending_confirmation"})
        assert status == 200
        listed = {}
        for item in response["data"]:
            listed[item["withdrawal_key"]] = item["client_key"]
        assert listed == {first_key: first_client_key, second_key: second_client_key}

    def test_paginates_without_repeating_or_skipping(self):
        DbUtils.rollback()
        Mock().clear()
        client_key, account_key = open_account_with_balance("100.00")

        created_keys = []
        for _ in range(3):
            withdrawal_key, _idempotency_key = ObjectGenerator.create_withdrawal_with_status(
                client_key, account_key, "completed", amount="5.00"
            )
            created_keys.append(withdrawal_key)

        status, first_page = RequestGenerator.GET_withdrawals({"limit": "2", "page": "0"})
        assert status == 200
        assert len(first_page["data"]) == 2
        assert first_page["is_last_page"] is False

        status, second_page = RequestGenerator.GET_withdrawals({"limit": "2", "page": "1"})
        assert status == 200
        assert len(second_page["data"]) == 1
        assert second_page["is_last_page"] is True

        listed_keys = values_of(first_page["data"] + second_page["data"], "withdrawal_key")
        assert sorted(listed_keys) == sorted(created_keys)

    def test_lists_nothing_when_there_are_no_withdrawals(self):
        DbUtils.rollback()

        status, response = RequestGenerator.GET_withdrawals()
        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_schema_refuses_malformed_query_params(self):
        crooked_params = [
            {"parametro_que_nao_existe": "1"},
            {"status": "failed"},
            {"status": "PENDING_CONFIRMATION"},
            {"limit": "0"},
            {"limit": "101"},
            {"page": "-1"},
        ]
        for params in crooked_params:
            status, response = RequestGenerator.GET_withdrawals(params)

            assert status == 400, f"os parâmetros {params} foram aceitos"
            assert response["code"] == "QIT000001"
