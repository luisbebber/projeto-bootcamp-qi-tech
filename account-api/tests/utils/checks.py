from decimal import Decimal

from tests.utils.mock_utils import Mock
from tests.utils.request_generator import RequestGenerator


def get_balance(client_key: str, account_key: str) -> str:
    _status, response = RequestGenerator.GET_account(client_key, account_key)

    return response["balance"]


def transfer_fee_requests(client_key: str) -> list:
    received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")

    transfer_requests = []
    for received_request in received_requests:
        if received_request["body"]["json"]["fee_type"] == "transfer":
            transfer_requests.append(received_request)

    return transfer_requests


def spi_withdrawal_requests() -> list:
    return Mock().retrieve_requests("POST", "/spi-api/withdrawal")


def values_of(items: list, field: str) -> list:
    values = []
    for item in items:
        values.append(item[field])

    return values


def rows_of(items: list, *fields: str) -> list:
    rows = []
    for item in items:
        row = []
        for field in fields:
            row.append(item[field])
        rows.append(tuple(row))

    return rows


def sum_of_amounts(entries: list) -> Decimal:
    total = Decimal("0")
    for entry in entries:
        total = total + Decimal(entry["amount"])

    return total
