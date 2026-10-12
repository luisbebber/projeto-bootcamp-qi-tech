from uuid import uuid4

from tests.utils import ObjectGenerator, RequestGenerator
from tests.utils.mock_generator import ClientApiMock, FeeApiMock
from tests.utils.mock_utils import Mock


class TestClientConfigurationCreate:

    def test_configures_client(self):
        Mock().clear()
        client_key = str(uuid4())

        ClientApiMock.GET_client(client_key)
        FeeApiMock.GET_fee_configuration(client_key)

        status, response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 201
        assert response == {"client_key": client_key}

        for path in [f"/client-api/client/{client_key}", f"/fee-api/client/{client_key}/fee_configuration"]:
            received_requests = Mock().retrieve_requests("GET", path)
            assert len(received_requests) == 1
            sent_token = received_requests[0]["headers"]["INTERNAL-TOKEN"]
            assert len(sent_token) == 1
            assert sent_token[0] != ""

    def test_refuses_already_configured_client(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        Mock().clear()
        ClientApiMock.GET_client(client_key)
        FeeApiMock.GET_fee_configuration(client_key)

        status, response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 409
        assert response["code"] == "QIT001001"

        assert Mock().retrieve_requests("GET", f"/client-api/client/{client_key}") == []
        assert Mock().retrieve_requests("GET", f"/fee-api/client/{client_key}/fee_configuration") == []

    def test_client_not_found_in_client_api(self):
        Mock().clear()
        client_key = str(uuid4())

        ClientApiMock.GET_client_not_found(client_key)
        FeeApiMock.GET_fee_configuration(client_key)

        status, response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 404
        assert response["code"] == "QIT001002"

        received_requests = Mock().retrieve_requests("GET", f"/fee-api/client/{client_key}/fee_configuration")
        assert received_requests == []

    def test_refuses_inactive_client(self):
        Mock().clear()
        client_key = str(uuid4())

        ClientApiMock.GET_client(client_key, status="inactivated")
        FeeApiMock.GET_fee_configuration(client_key)

        status, response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 409
        assert response["code"] == "QIT001003"

        received_requests = Mock().retrieve_requests("GET", f"/fee-api/client/{client_key}/fee_configuration")
        assert received_requests == []

    def test_refuses_client_without_fees(self):
        Mock().clear()
        client_key = str(uuid4())

        ClientApiMock.GET_client(client_key)
        FeeApiMock.GET_fee_configuration_not_found(client_key)

        status, response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 409
        assert response["code"] == "QIT001004"

    def test_client_api_failure(self):
        failures = [
            ClientApiMock.GET_client_server_error,
            ClientApiMock.GET_client_connection_dropped,
        ]

        for teach_failure in failures:
            Mock().clear()
            client_key = str(uuid4())

            teach_failure(client_key)
            FeeApiMock.GET_fee_configuration(client_key)

            status, response = RequestGenerator.POST_client_configuration(client_key)
            assert status == 502, f"{teach_failure.__name__} answered {status}"
            assert response["code"] == "QIT001005"

            received_requests = Mock().retrieve_requests("GET", f"/fee-api/client/{client_key}/fee_configuration")
            assert received_requests == []

    def test_fee_api_failure(self):
        for teach_failure in [FeeApiMock.GET_fee_configuration_server_error, FeeApiMock.GET_fee_configuration_connection_dropped]:
            Mock().clear()
            client_key = str(uuid4())

            ClientApiMock.GET_client(client_key)
            teach_failure(client_key)

            status, response = RequestGenerator.POST_client_configuration(client_key)
            assert status == 502, f"{teach_failure.__name__} answered {status}"
            assert response["code"] == "QIT001006"

            Mock().clear()
            ClientApiMock.GET_client(client_key)
            FeeApiMock.GET_fee_configuration(client_key)

            status, _response = RequestGenerator.POST_client_configuration(client_key)
            assert status == 201
