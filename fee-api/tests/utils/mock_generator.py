from tests.utils.mock_utils import BaseExpectation, Mock


class ClientApiMock:

    @staticmethod
    def GET_client(client_key: str, status: str = "active"):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/client-api/client/{client_key}",
                status_code=200,
                response_json={
                    "client_key": client_key,
                    "name": "Empresa Exemplo Ltda",
                    "document_number": "17895646000187",
                    "operation": "delivery",
                    "status": status,
                    "status_events": [{"status": status, "created_at": "2026-10-01T10:00:00"}],
                    "created_at": "2026-10-01T10:00:00",
                },
            )
        )

    @staticmethod
    def GET_client_not_found(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/client-api/client/{client_key}",
                status_code=404,
                response_json={
                    "title": "Client not found",
                    "description": f"Client with key {client_key} was not found.",
                    "translation": f"O cliente com chave {client_key} não foi encontrado.",
                    "code": "QIT001001",
                },
                priority=1,
            )
        )

    @staticmethod
    def GET_client_server_error(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/client-api/client/{client_key}",
                status_code=500,
                response_json={"code": "INTERNAL_ERROR", "description": "Unexpected error in the client-api."},
                priority=1,
            )
        )

    @staticmethod
    def GET_client_connection_dropped(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_error(
                "GET",
                f"/client-api/client/{client_key}",
                error_json={"dropConnection": True},
                priority=1,
            )
        )
