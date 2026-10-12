from decimal import Decimal

from connectors.rest_connector import BaseConnectorResponse, RestConnector
from constants import SPI_API_INTERNAL_TOKEN, SPI_API_TIMEOUT, SPI_API_URL


class SpiApiConnector(RestConnector):

    def __init__(self) -> None:
        super().__init__(
            class_name=__name__,
            base_url=SPI_API_URL,
            timeout=SPI_API_TIMEOUT,
            internal_token=SPI_API_INTERNAL_TOKEN,
        )

    def post_withdrawal(self, idempotency_key: str, amount: Decimal, receiver_data: dict) -> BaseConnectorResponse:
        payload = {
            "idempotency_key": idempotency_key,
            "amount": f"{amount:.2f}",
            "receiver_data": receiver_data,
        }

        return self.send(endpoint="/withdrawal", method="POST", payload=payload)
