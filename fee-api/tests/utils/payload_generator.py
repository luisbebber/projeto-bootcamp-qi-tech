from uuid import uuid4


class PayloadGenerator:

    @staticmethod
    def create_fee_payload(fee_type: str = None, idempotency_key: str = None) -> dict:
        if fee_type is None:
            fee_type = "transfer"

        if idempotency_key is None:
            idempotency_key = str(uuid4())

        return {
            "fee_type": fee_type,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def create_fee_configuration_payload(transfer_amount: str = None, account_opening_amount: str = None) -> dict:
        if transfer_amount is None:
            transfer_amount = "0.50"

        if account_opening_amount is None:
            account_opening_amount = "2.00"

        return {
            "transfer_amount": transfer_amount,
            "account_opening_amount": account_opening_amount,
        }

    @staticmethod
    def update_fee_configuration_payload(transfer_amount: str = None, account_opening_amount: str = None) -> dict:
        payload = {}

        if transfer_amount is not None:
            payload["transfer_amount"] = transfer_amount

        if account_opening_amount is not None:
            payload["account_opening_amount"] = account_opening_amount

        return payload

    @staticmethod
    def create_charge_payload(month: str) -> dict:
        return {"month": month}
