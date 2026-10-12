from tests.utils import DbUtils, ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import values_of
from tests.utils.mock_generator import FeeApiMock
from tests.utils.mock_utils import Mock


def open_account() -> tuple:
    client_key = ObjectGenerator.configure_client()
    account_key = ObjectGenerator.create_account(client_key)["account_key"]

    return client_key, account_key


def create_completed_deposit(client_key: str, account_key: str, amount: str = "10.00") -> str:
    return ObjectGenerator.create_deposit(client_key, account_key, amount=amount)["deposit_key"]


def create_pending_fee_deposit(client_key: str, account_key: str, amount: str = "10.00") -> str:
    FeeApiMock.POST_fee_not_found(client_key)

    payload = PayloadGenerator.create_deposit_payload(amount=amount)
    status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
    assert status == 201

    return response["deposit_key"]


class TestDepositsList:

    def test_lists_deposits_by_status(self):
        DbUtils.rollback()
        Mock().clear()
        client_key, account_key = open_account()

        completed_key = create_completed_deposit(client_key, account_key, amount="10.00")
        pending_fee_key = create_pending_fee_deposit(client_key, account_key, amount="20.50")

        status, response = RequestGenerator.GET_deposits()
        assert status == 200
        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True

        pending_fee_item, completed_item = response["data"]
        assert pending_fee_item == {
            "deposit_key": pending_fee_key,
            "client_key": client_key,
            "account_key": account_key,
            "amount": "20.50",
            "status": "pending_fee",
            "created_at": pending_fee_item["created_at"],
        }
        assert completed_item["deposit_key"] == completed_key
        assert completed_item["status"] == "completed"

        status, response = RequestGenerator.GET_deposits({"status": "pending_fee"})
        assert status == 200
        assert response["data"] == [pending_fee_item]

        status, response = RequestGenerator.GET_deposits({"status": "completed"})
        assert status == 200
        assert response["data"] == [completed_item]

    def test_lists_deposits_of_every_client(self):
        DbUtils.rollback()
        Mock().clear()
        first_client_key, first_account_key = open_account()
        second_client_key, second_account_key = open_account()

        first_key = create_pending_fee_deposit(first_client_key, first_account_key)
        second_key = create_pending_fee_deposit(second_client_key, second_account_key)

        status, response = RequestGenerator.GET_deposits({"status": "pending_fee"})
        assert status == 200
        listed = {}
        for item in response["data"]:
            listed[item["deposit_key"]] = item["client_key"]
        assert listed == {first_key: first_client_key, second_key: second_client_key}

    def test_paginates_without_repeating_or_skipping(self):
        DbUtils.rollback()
        Mock().clear()
        client_key, account_key = open_account()

        created_keys = []
        for _ in range(3):
            created_keys.append(create_completed_deposit(client_key, account_key))

        status, first_page = RequestGenerator.GET_deposits({"limit": "2", "page": "0"})
        assert status == 200
        assert len(first_page["data"]) == 2
        assert first_page["is_last_page"] is False

        status, second_page = RequestGenerator.GET_deposits({"limit": "2", "page": "1"})
        assert status == 200
        assert len(second_page["data"]) == 1
        assert second_page["is_last_page"] is True

        listed_keys = values_of(first_page["data"] + second_page["data"], "deposit_key")
        assert sorted(listed_keys) == sorted(created_keys)

    def test_lists_nothing_when_there_are_no_deposits(self):
        DbUtils.rollback()

        status, response = RequestGenerator.GET_deposits()
        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_schema_refuses_malformed_query_params(self):
        crooked_params = [
            {"parametro_que_nao_existe": "1"},
            {"status": "failed"},
            {"status": "PENDING_FEE"},
            {"limit": "0"},
            {"limit": "101"},
            {"page": "-1"},
        ]
        for params in crooked_params:
            status, response = RequestGenerator.GET_deposits(params)

            assert status == 400, f"os parâmetros {params} foram aceitos"
            assert response["code"] == "QIT000001"
