from tests.utils.payload_generator import PayloadGenerator
from tests.utils.request_generator import RequestGenerator


class ObjectGenerator:
    @staticmethod
    def create_client(name: str = None, document_number: str = None, operation: str = None) -> dict:
        client_payload = PayloadGenerator.create_client_payload(name, document_number, operation)

        status, response = RequestGenerator.POST_client(client_payload)
        assert status == 201

        return response

    @staticmethod
    def update_client_status(client_key: str, new_status: str) -> dict:
        status_payload = PayloadGenerator.create_client_status_payload(new_status)

        status, response = RequestGenerator.PATCH_client(client_key, status_payload)
        assert status == 200

        return response
