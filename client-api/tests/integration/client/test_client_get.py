from uuid import uuid4

from tests.utils import ObjectGenerator, RandomGenerator, RequestGenerator


class TestClientGet:

    def test_gets_client(self):
        document_number = RandomGenerator.generate_cnpj()
        operation = RandomGenerator.generate_operation()
        client_key = ObjectGenerator.create_client(
            name="Uber do Brasil Tecnologia Ltda", document_number=document_number, operation=operation
        )["client_key"]

        status, response = RequestGenerator.GET_client(client_key)
        assert status == 200

        created_at = response["created_at"]
        event_created_at = response["status_events"][0]["created_at"]
        assert created_at is not None
        assert event_created_at is not None

        assert response == {
            "client_key": client_key,
            "name": "Uber do Brasil Tecnologia Ltda",
            "document_number": document_number,
            "operation": operation,
            "status": "active",
            "status_events": [
                {"status": "active", "created_at": event_created_at},
            ],
            "created_at": created_at,
        }

    def test_refuses_unknown_client_key(self):
        client_key = str(uuid4())

        status, response = RequestGenerator.GET_client(client_key)

        assert status == 404
        assert response == {
            "title": "Client not found",
            "description": f"Client with key {client_key} was not found.",
            "translation": f"O cliente com chave {client_key} não foi encontrado.",
            "code": "QIT001003",
        }
