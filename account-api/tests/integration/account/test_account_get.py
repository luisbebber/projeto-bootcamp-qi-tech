from uuid import uuid4

from tests.utils import ObjectGenerator, RandomGenerator, RequestGenerator
from tests.utils.mock_utils import Mock


class TestAccountGet:

    def test_gets_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        account_key = ObjectGenerator.create_account(
            client_key, name="Joana Souza", document_number=document_number
        )["account_key"]

        status, response = RequestGenerator.GET_account(client_key, account_key)
        assert status == 200

        created_at = response["created_at"]
        event_created_at = response["status_events"][0]["created_at"]
        assert created_at is not None
        assert event_created_at is not None

        assert response == {
            "account_key": account_key,
            "name": "Joana Souza",
            "document_number": document_number,
            "balance": "0.00",
            "status": "active",
            "status_events": [
                {"status": "active", "created_at": event_created_at},
            ],
            "created_at": created_at,
        }

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        status, response = RequestGenerator.GET_account(client_key, str(uuid4()))
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        owner_client_key = ObjectGenerator.configure_client()
        other_client_key = ObjectGenerator.configure_client()

        account_key = ObjectGenerator.create_account(owner_client_key)["account_key"]

        status, _response = RequestGenerator.GET_account(owner_client_key, account_key)
        assert status == 200

        status, response = RequestGenerator.GET_account(other_client_key, account_key)
        assert status == 404
        assert response["code"] == "QIT001010"
