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


class FeeApiMock:

    @staticmethod
    def GET_fee_configuration(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/fee-api/client/{client_key}/fee_configuration",
                status_code=200,
                response_json={
                    "client_key": client_key,
                    "fees": [
                        {"fee_type": "transfer", "amount": "0.50", "status": "active"},
                        {"fee_type": "account_opening", "amount": "2.00", "status": "active"},
                    ],
                },
            )
        )

    @staticmethod
    def GET_fee_configuration_not_found(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/fee-api/client/{client_key}/fee_configuration",
                status_code=404,
                response_json={
                    "title": "Client not configured",
                    "description": f"Client with key {client_key} has no fees.",
                    "translation": f"O cliente com chave {client_key} não tem taxas cadastradas.",
                    "code": "QIT001001",
                },
                priority=1,
            )
        )
    @staticmethod
    def POST_fee(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                f"/fee-api/client/{client_key}/fee",
                status_code=201,
                response_json={"fee_key": "00000000-0000-0000-0000-000000000000"},
            )
        )

    @staticmethod
    def POST_fee_not_found(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                f"/fee-api/client/{client_key}/fee",
                status_code=404,
                response_json={
                    "title": "Client not configured",
                    "description": f"Client with key {client_key} has no fees.",
                    "translation": f"O cliente com chave {client_key} não tem taxas cadastradas.",
                    "code": "QIT001001",
                },
                priority=1,
            )
        )

    @staticmethod
    def GET_fee_configuration_server_error(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/fee-api/client/{client_key}/fee_configuration",
                status_code=500,
                response_json={"code": "INTERNAL_ERROR", "description": "Unexpected error in the fee-api."},
                priority=1,
            )
        )

    @staticmethod
    def GET_fee_configuration_connection_dropped(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_error(
                "GET",
                f"/fee-api/client/{client_key}/fee_configuration",
                error_json={"dropConnection": True},
                priority=1,
            )
        )

    @staticmethod
    def POST_fee_connection_dropped(client_key: str):
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_error(
                "POST",
                f"/fee-api/client/{client_key}/fee",
                error_json={"dropConnection": True},
                priority=1,
            )
        )


class SpiApiMock:

    @staticmethod
    def POST_withdrawal():
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                "/spi-api/withdrawal",
                status_code=201,
                response_json={"status": "sent"},
            )
        )

    @staticmethod
    def POST_withdrawal_refused():
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                "/spi-api/withdrawal",
                status_code=422,
                response_json={"status": "rejected", "description": "Target account number is invalid."},
                priority=1,
            )
        )

    @staticmethod
    def POST_withdrawal_pending():
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                "/spi-api/withdrawal",
                status_code=202,
                response_json={"status": "pending"},
                priority=1,
            )
        )

    @staticmethod
    def POST_withdrawal_server_error():
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "POST",
                "/spi-api/withdrawal",
                status_code=500,
                response_json={"code": "INTERNAL_ERROR", "description": "Unexpected error in the SPI service."},
                priority=1,
            )
        )

    @staticmethod
    def POST_withdrawal_connection_dropped():
        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_error(
                "POST",
                "/spi-api/withdrawal",
                error_json={"dropConnection": True},
                priority=1,
            )
        )
