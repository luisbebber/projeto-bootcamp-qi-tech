from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator, ResponseUtils


class TestClientUpdate:

    def test_inactivates_client(self):
        client_key = ObjectGenerator.create_client()["client_key"]

        status, response = RequestGenerator.PATCH_client(client_key, PayloadGenerator.create_client_status_payload("inactivated"))

        assert status == 200
        assert response == {"client_key": client_key, "status": "inactivated"}

        status, client = RequestGenerator.GET_client(client_key)
        assert status == 200
        assert client["status"] == "inactivated"
        assert ResponseUtils.status_trail(client) == ["active", "inactivated"]

    def test_reactivates_client_with_the_same_client_key(self):
        client_key = ObjectGenerator.create_client()["client_key"]
        ObjectGenerator.update_client_status(client_key, "inactivated")

        status, response = RequestGenerator.PATCH_client(client_key, PayloadGenerator.create_client_status_payload("active"))

        assert status == 200
        assert response == {"client_key": client_key, "status": "active"}

        status, client = RequestGenerator.GET_client(client_key)
        assert status == 200
        assert client["client_key"] == client_key
        assert client["status"] == "active"
        assert ResponseUtils.status_trail(client) == ["active", "inactivated", "active"]

    def test_schema_refuses_malformed_body(self):
        client_key = ObjectGenerator.create_client()["client_key"]

        status, response = RequestGenerator.PATCH_client(client_key, {})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_client_status_payload()
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.PATCH_client(client_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        for crooked_value in ["", "terminated", "ACTIVE", "Inactivated", 1, None]:
            payload = PayloadGenerator.create_client_status_payload(crooked_value)

            status, response = RequestGenerator.PATCH_client(client_key, payload)

            assert status == 400, f"o status '{crooked_value}' foi aceito"
            assert response["code"] == "QIT000001"

        status, client = RequestGenerator.GET_client(client_key)
        assert status == 200
        assert client["status"] == "active"
        assert ResponseUtils.status_trail(client) == ["active"]

    def test_refuses_unknown_client_key(self):
        status, response = RequestGenerator.PATCH_client(str(uuid4()), PayloadGenerator.create_client_status_payload())

        assert status == 404
        assert response["code"] == "QIT001003"

    def test_refuses_status_the_client_already_has(self):
        client_key = ObjectGenerator.create_client()["client_key"]

        status, response = RequestGenerator.PATCH_client(client_key, PayloadGenerator.create_client_status_payload("active"))
        assert status == 409
        assert response["code"] == "QIT001004"

        ObjectGenerator.update_client_status(client_key, "inactivated")
        status, response = RequestGenerator.PATCH_client(client_key, PayloadGenerator.create_client_status_payload("inactivated"))
        assert status == 409
        assert response["code"] == "QIT001004"

        status, client = RequestGenerator.GET_client(client_key)
        assert status == 200
        assert client["status"] == "inactivated"
        assert ResponseUtils.status_trail(client) == ["active", "inactivated"]

    def test_changes_only_the_client_asked(self):
        document_number = RandomGenerator.generate_cnpj()
        first_client_key = ObjectGenerator.create_client(document_number=document_number, operation="uber")["client_key"]
        second_client_key = ObjectGenerator.create_client(document_number=document_number, operation="uber-eats")["client_key"]

        ObjectGenerator.update_client_status(first_client_key, "inactivated")

        _, first_client = RequestGenerator.GET_client(first_client_key)
        _, second_client = RequestGenerator.GET_client(second_client_key)
        assert first_client["status"] == "inactivated"
        assert second_client["status"] == "active"
