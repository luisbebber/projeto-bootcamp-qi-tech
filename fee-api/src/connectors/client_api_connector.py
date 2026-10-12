from connectors.rest_connector import BaseConnectorResponse, RestConnector
from constants import CLIENT_API_INTERNAL_TOKEN, CLIENT_API_TIMEOUT, CLIENT_API_URL


class ClientApiConnector(RestConnector):

    def __init__(self) -> None:
        super().__init__(
            class_name=__name__,
            base_url=CLIENT_API_URL,
            timeout=CLIENT_API_TIMEOUT,
            internal_token=CLIENT_API_INTERNAL_TOKEN,
        )

    def get_client(self, client_key: str) -> BaseConnectorResponse:
        return self.send(endpoint=f"/client/{client_key}", method="GET")
