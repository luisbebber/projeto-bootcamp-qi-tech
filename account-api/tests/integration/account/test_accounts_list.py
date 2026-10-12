from tests.utils import ObjectGenerator, RandomGenerator, RequestGenerator
from tests.utils.checks import values_of
from tests.utils.mock_utils import Mock


class TestAccountsList:

    def test_lists_accounts_newest_first(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        first_document_number = RandomGenerator.generate_cpf()

        first_account_key = ObjectGenerator.create_account(
            client_key, name="Joana Souza", document_number=first_document_number
        )["account_key"]
        second_account_key = ObjectGenerator.create_account(client_key)["account_key"]

        status, response = RequestGenerator.GET_accounts(client_key)
        assert status == 200

        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True
        assert values_of(response["data"], "account_key") == [second_account_key, first_account_key]

        first_account = response["data"][1]
        assert first_account == {
            "account_key": first_account_key,
            "name": "Joana Souza",
            "document_number": first_document_number,
            "balance": "0.00",
            "status": "active",
            "created_at": first_account["created_at"],
        }

    def test_paginates_without_repeating_or_skipping(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        created_keys = []
        for _ in range(3):
            created_keys.append(ObjectGenerator.create_account(client_key)["account_key"])

        status, first_page = RequestGenerator.GET_accounts(client_key, {"limit": "2", "page": "0"})
        assert status == 200
        assert len(first_page["data"]) == 2
        assert first_page["is_last_page"] is False

        status, second_page = RequestGenerator.GET_accounts(client_key, {"limit": "2", "page": "1"})
        assert status == 200
        assert len(second_page["data"]) == 1
        assert second_page["is_last_page"] is True

        listed_keys = values_of(first_page["data"] + second_page["data"], "account_key")
        assert sorted(listed_keys) == sorted(created_keys)

    def test_lists_nothing_for_client_without_accounts(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        status, response = RequestGenerator.GET_accounts(client_key)
        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_does_not_list_accounts_of_another_client(self):
        Mock().clear()
        owner_client_key = ObjectGenerator.configure_client()
        other_client_key = ObjectGenerator.configure_client()

        owner_account_key = ObjectGenerator.create_account(owner_client_key)["account_key"]
        ObjectGenerator.create_account(other_client_key)

        status, response = RequestGenerator.GET_accounts(owner_client_key)
        assert status == 200
        assert values_of(response["data"], "account_key") == [owner_account_key]

    def test_refuses_unconfigured_client(self):
        Mock().clear()

        status, response = RequestGenerator.GET_accounts("00000000-0000-0000-0000-000000000000")
        assert status == 404
        assert response["code"] == "QIT001008"

    def test_schema_refuses_malformed_query_params(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        crooked_params = [
            {"parametro_que_nao_existe": "1"},
            {"limit": "0"},
            {"limit": "101"},
            {"limit": "abc"},
            {"page": "-1"},
            {"page": "abc"},
        ]
        for params in crooked_params:
            status, response = RequestGenerator.GET_accounts(client_key, params)

            assert status == 400, f"os parâmetros {params} foram aceitos"
            assert response["code"] == "QIT000001"
