from uuid import uuid4

from tests.utils.random_generator import RandomGenerator


class PayloadGenerator:

    @staticmethod
    def create_account_payload(
        name: str = None,
        document_number: str = None,
        idempotency_key: str = None,
    ) -> dict:
        if name is None:
            name = "Maria da Silva"

        if document_number is None:
            document_number = RandomGenerator.generate_cpf()

        if idempotency_key is None:
            idempotency_key = str(uuid4())

        return {
            "name": name,
            "document_number": document_number,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def create_account_status_payload(status: str = "closed") -> dict:
        return {"status": status}

    @staticmethod
    def create_deposit_payload(amount: str = None, idempotency_key: str = None) -> dict:
        if amount is None:
            amount = "126.97"

        if idempotency_key is None:
            idempotency_key = str(uuid4())

        return {"amount": amount, "idempotency_key": idempotency_key}

    @staticmethod
    def create_withdrawal_payload(amount: str = None, idempotency_key: str = None) -> dict:
        if amount is None:
            amount = "30.00"

        if idempotency_key is None:
            idempotency_key = str(uuid4())

        return {
            "amount": amount,
            "idempotency_key": idempotency_key,
            "receiver_data": {
                "ispb": "32402502",
                "account_branch": "0001",
                "account_number": "12345678",
                "account_digit": "3",
                "account_type": "checking",
                "owner_document_number": "52998224725",
                "owner_name": "Maria da Silva",
            },
        }

    @staticmethod
    def create_transfer_payload(
        origin_account_key: str, destination_account_key: str, amount: str = None, idempotency_key: str = None
    ) -> dict:
        if amount is None:
            amount = "30.00"

        if idempotency_key is None:
            idempotency_key = str(uuid4())

        return {
            "origin_account_key": origin_account_key,
            "destination_account_key": destination_account_key,
            "amount": amount,
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def create_deposit_status_payload(status: str = "completed") -> dict:
        return {"status": status}

    @staticmethod
    def create_withdrawal_status_payload(status: str = "completed") -> dict:
        return {"status": status}
