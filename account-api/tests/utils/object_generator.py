from uuid import uuid4

from tests.utils.mock_generator import ClientApiMock, FeeApiMock, SpiApiMock
from tests.utils.mock_utils import Mock
from tests.utils.payload_generator import PayloadGenerator
from tests.utils.request_generator import RequestGenerator


class ObjectGenerator:
    @staticmethod
    def configure_client() -> str:
        client_key = str(uuid4())

        ClientApiMock.GET_client(client_key)
        FeeApiMock.GET_fee_configuration(client_key)

        status, _response = RequestGenerator.POST_client_configuration(client_key)
        assert status == 201

        return client_key

    @staticmethod
    def create_account(
        client_key: str, name: str = None, document_number: str = None, idempotency_key: str = None
    ) -> dict:
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_account_payload(
            name=name, document_number=document_number, idempotency_key=idempotency_key
        )

        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 201

        return response

    @staticmethod
    def close_account(client_key: str, account_key: str) -> dict:
        payload = PayloadGenerator.create_account_status_payload()

        status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)
        assert status == 200

        return response

    @staticmethod
    def create_deposit(client_key: str, account_key: str, amount: str = None) -> dict:
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_deposit_payload(amount=amount)

        status, response = RequestGenerator.POST_deposit(client_key, account_key, payload)
        assert status == 201

        return response

    @staticmethod
    def create_withdrawal(client_key: str, account_key: str, amount: str = None) -> dict:
        SpiApiMock.POST_withdrawal()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_withdrawal_payload(amount=amount)

        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 201

        return response

    @staticmethod
    def create_transfer(client_key: str, origin_account_key: str, destination_account_key: str, amount: str = None) -> dict:
        payload = PayloadGenerator.create_transfer_payload(origin_account_key, destination_account_key, amount=amount)

        status, response = RequestGenerator.POST_transfer(client_key, payload)
        assert status == 201

        return response

    @staticmethod
    def create_withdrawal_with_status(client_key: str, account_key: str, final_status: str, amount: str = None) -> tuple:
        Mock().clear()

        if final_status == "completed":
            SpiApiMock.POST_withdrawal()
            FeeApiMock.POST_fee(client_key)
        elif final_status == "pending_fee":
            SpiApiMock.POST_withdrawal()
            FeeApiMock.POST_fee_not_found(client_key)
        elif final_status == "pending_confirmation":
            SpiApiMock.POST_withdrawal_pending()
        elif final_status == "reversed":
            SpiApiMock.POST_withdrawal_refused()
        else:
            raise ValueError(f"status de saque desconhecido: {final_status}")

        payload = PayloadGenerator.create_withdrawal_payload(amount=amount)

        status, response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status in (201, 202)

        return response["withdrawal_key"], payload["idempotency_key"]
