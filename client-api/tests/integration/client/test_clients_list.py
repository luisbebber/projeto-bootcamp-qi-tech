from tests.utils import DbUtils, ObjectGenerator, RandomGenerator, RequestGenerator, ResponseUtils


class TestClientsList:

    def test_lists_clients_of_a_document_number_newest_first(self):
        document_number = RandomGenerator.generate_cnpj()
        first_client_key = ObjectGenerator.create_client(
            name="Uber do Brasil Tecnologia Ltda", document_number=document_number, operation="uber"
        )["client_key"]
        second_client_key = ObjectGenerator.create_client(document_number=document_number, operation="uber-eats")["client_key"]

        status, response = RequestGenerator.GET_clients({"document_number": document_number})
        assert status == 200

        assert response["limit"] == 10
        assert response["page"] == 0
        assert response["is_last_page"] is True
        assert ResponseUtils.client_keys(response["data"]) == [second_client_key, first_client_key]

        first_client = response["data"][1]
        assert first_client == {
            "client_key": first_client_key,
            "name": "Uber do Brasil Tecnologia Ltda",
            "document_number": document_number,
            "operation": "uber",
            "status": "active",
            "created_at": first_client["created_at"],
        }

    def test_filter_returns_only_the_document_number_asked(self):
        document_number = RandomGenerator.generate_cnpj()
        client_key = ObjectGenerator.create_client(document_number=document_number)["client_key"]
        ObjectGenerator.create_client()

        status, response = RequestGenerator.GET_clients({"document_number": document_number})

        assert status == 200
        assert ResponseUtils.client_keys(response["data"]) == [client_key]

    def test_document_number_without_match_returns_empty_list(self):
        status, response = RequestGenerator.GET_clients({"document_number": RandomGenerator.generate_cnpj()})

        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_paginates_without_repeating_or_skipping(self):
        document_number = RandomGenerator.generate_cnpj()
        created_keys = []
        for _ in range(3):
            created_keys.append(ObjectGenerator.create_client(document_number=document_number)["client_key"])

        status, first_page = RequestGenerator.GET_clients({"document_number": document_number, "limit": "2", "page": "0"})
        assert status == 200
        assert len(first_page["data"]) == 2
        assert first_page["limit"] == 2
        assert first_page["page"] == 0
        assert first_page["is_last_page"] is False

        status, second_page = RequestGenerator.GET_clients({"document_number": document_number, "limit": "2", "page": "1"})
        assert status == 200
        assert len(second_page["data"]) == 1
        assert second_page["page"] == 1
        assert second_page["is_last_page"] is True

        listed_keys = ResponseUtils.client_keys(first_page["data"] + second_page["data"])
        assert listed_keys == list(reversed(created_keys))

    def test_lists_all_clients_without_filter(self):
        DbUtils.rollback()
        first_client_key = ObjectGenerator.create_client()["client_key"]
        second_client_key = ObjectGenerator.create_client()["client_key"]

        status, response = RequestGenerator.GET_clients()

        assert status == 200
        assert ResponseUtils.client_keys(response["data"]) == [second_client_key, first_client_key]

    def test_schema_refuses_malformed_query(self):
        crooked_params = [
            {"parametro_que_nao_existe": "1"},
            {"limit": "0"},
            {"limit": "101"},
            {"limit": "abc"},
            {"limit": ""},
            {"page": "-1"},
            {"page": "abc"},
            {"document_number": "1122233300018"},
            {"document_number": "11.222.333/0001-81"},
            {"document_number": "12abc34501de35"},
            {"document_number": ""},
        ]
        for params in crooked_params:
            status, response = RequestGenerator.GET_clients(params)

            assert status == 400, f"a query {params} foi aceita"
            assert response["code"] == "QIT000001"
