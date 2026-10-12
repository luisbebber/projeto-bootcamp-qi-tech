from connectors.rest_connector import BaseConnectorResponse, RestConnector
from constants import FEE_API_INTERNAL_TOKEN, FEE_API_TIMEOUT, FEE_API_URL


class FeeApiConnector(RestConnector):

    def __init__(self) -> None:
        super().__init__(
            class_name=__name__,
            base_url=FEE_API_URL,
            timeout=FEE_API_TIMEOUT,
            internal_token=FEE_API_INTERNAL_TOKEN,
        )

    def get_fee_configuration(self, client_key: str) -> BaseConnectorResponse:
        return self.send(endpoint=f"/client/{client_key}/fee_configuration", method="GET")

    def post_fee(self, client_key: str, fee_type: str, idempotency_key: str) -> BaseConnectorResponse:
        payload = {"fee_type": fee_type, "idempotency_key": idempotency_key}

        return self.send(endpoint=f"/client/{client_key}/fee", method="POST", payload=payload)
