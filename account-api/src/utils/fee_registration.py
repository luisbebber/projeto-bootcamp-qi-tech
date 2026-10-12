import requests


def register_fee(fee_api_connector, logger, client_key: str, fee_type: str, idempotency_key: str) -> bool:
    try:
        response = fee_api_connector.post_fee(client_key, fee_type, idempotency_key)
    except requests.RequestException:
        logger.error(f"A fee-api não respondeu ao registro da taxa {fee_type} da operação {idempotency_key}")
        return False

    if response.status != 201:
        logger.error(f"A fee-api respondeu {response.status} ao registro da taxa {fee_type} da operação {idempotency_key}")
        return False

    return True
