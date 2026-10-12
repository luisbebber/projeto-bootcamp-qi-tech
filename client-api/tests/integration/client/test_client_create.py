from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator, ResponseUtils


class TestClientCreate:

    def test_creates_client(self):
        payload = PayloadGenerator.create_client_payload()

        status, response = RequestGenerator.POST_client(payload)

        assert status == 201
        client_key = response["client_key"]
        assert response == {"client_key": client_key, "status": "active"}

        status, client = RequestGenerator.GET_client(client_key)
        assert status == 200
        assert client["name"] == payload["name"]
        assert client["document_number"] == payload["document_number"]
        assert client["operation"] == payload["operation"]
        assert client["status"] == "active"
        assert ResponseUtils.status_trail(client) == ["active"]

    def test_creates_client_with_alphanumeric_document_number(self):
        payload = PayloadGenerator.create_client_payload(document_number="12ABC34501DE35")

        status, response = RequestGenerator.POST_client(payload)

        assert status == 201
        assert response["status"] == "active"

        status, client = RequestGenerator.GET_client(response["client_key"])
        assert status == 200
        assert client["document_number"] == "12ABC34501DE35"

    def test_creates_client_with_numeric_document_number(self):
        payload = PayloadGenerator.create_client_payload(document_number="11222333000181")

        status, response = RequestGenerator.POST_client(payload)

        assert status == 201
        assert response["status"] == "active"

        status, client = RequestGenerator.GET_client(response["client_key"])
        assert status == 200
        assert client["document_number"] == "11222333000181"

    def test_schema_refuses_malformed_body(self):
        status, response = RequestGenerator.POST_client({})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_client_payload()
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_client(payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        for field in ["name", "document_number", "operation"]:
            payload = PayloadGenerator.create_client_payload()
            del payload[field]

            status, response = RequestGenerator.POST_client(payload)

            assert status == 400, f"o campo '{field}' é obrigatório e passou sem ele"
            assert response["code"] == "QIT000001"

        crooked_fields = [
            ("name", ""),
            ("name", "a" * 256),
            ("name", 123),
            ("document_number", "1122233300018"),
            ("document_number", "112223330001811"),
            ("document_number", "11.222.333/0001-81"),
            ("document_number", "12abc34501de35"),
            ("document_number", "12ABC34501DEAB"),
            ("document_number", ""),
            ("operation", ""),
            ("operation", "Uber"),
            ("operation", "uber_eats"),
            ("operation", "uber eats"),
            ("operation", "a" * 51),
        ]
        for field, crooked_value in crooked_fields:
            payload = PayloadGenerator.create_client_payload()
            payload[field] = crooked_value

            status, response = RequestGenerator.POST_client(payload)

            assert status == 400, f"o campo '{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

    def test_refuses_invalid_document_number(self):
        invalid_document_numbers = [
            "11222333000182",
            "12ABC34501DE36",
            "11222333000191",
            "00000000000000",
            "11111111111111",
        ]
        for document_number in invalid_document_numbers:
            payload = PayloadGenerator.create_client_payload(document_number=document_number)

            status, response = RequestGenerator.POST_client(payload)

            assert status == 422, f"o CNPJ '{document_number}' foi aceito"
            assert response["code"] == "QIT001001"

            status, clients = RequestGenerator.GET_clients({"document_number": document_number})
            assert status == 200
            assert clients["data"] == []

    def test_refuses_duplicated_document_number_and_operation(self):
        document_number = RandomGenerator.generate_cnpj()
        operation = RandomGenerator.generate_operation()
        ObjectGenerator.create_client(document_number=document_number, operation=operation)

        payload = PayloadGenerator.create_client_payload(name="Outro nome", document_number=document_number, operation=operation)
        status, response = RequestGenerator.POST_client(payload)

        assert status == 409
        assert response["code"] == "QIT001002"

        status, clients = RequestGenerator.GET_clients({"document_number": document_number})
        assert status == 200
        assert len(clients["data"]) == 1
        assert clients["data"][0]["name"] != "Outro nome"

    def test_refuses_duplicated_operation_even_if_inactivated(self):
        document_number = RandomGenerator.generate_cnpj()
        operation = RandomGenerator.generate_operation()
        client_key = ObjectGenerator.create_client(document_number=document_number, operation=operation)["client_key"]
        ObjectGenerator.update_client_status(client_key, "inactivated")

        payload = PayloadGenerator.create_client_payload(document_number=document_number, operation=operation)
        status, response = RequestGenerator.POST_client(payload)

        assert status == 409
        assert response["code"] == "QIT001002"

        status, clients = RequestGenerator.GET_clients({"document_number": document_number})
        assert status == 200
        assert ResponseUtils.client_keys_and_statuses(clients["data"]) == [(client_key, "inactivated")]

    def test_accepts_same_document_number_with_another_operation(self):
        document_number = RandomGenerator.generate_cnpj()
        first_client = ObjectGenerator.create_client(document_number=document_number, operation="uber")
        second_client = ObjectGenerator.create_client(document_number=document_number, operation="uber-eats")

        assert first_client["client_key"] != second_client["client_key"]

        _, first = RequestGenerator.GET_client(first_client["client_key"])
        _, second = RequestGenerator.GET_client(second_client["client_key"])
        assert first["document_number"] == second["document_number"] == document_number
        assert first["operation"] == "uber"
        assert second["operation"] == "uber-eats"

    def test_accepts_same_operation_with_another_document_number(self):
        operation = RandomGenerator.generate_operation()
        first_client = ObjectGenerator.create_client(operation=operation)
        second_client = ObjectGenerator.create_client(operation=operation)

        assert first_client["client_key"] != second_client["client_key"]

        _, first = RequestGenerator.GET_client(first_client["client_key"])
        _, second = RequestGenerator.GET_client(second_client["client_key"])
        assert first["operation"] == second["operation"] == operation
        assert first["document_number"] != second["document_number"]
