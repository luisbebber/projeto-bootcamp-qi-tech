from uuid import uuid4

from tests.utils.db_utils import DbUtils
from tests.utils.mock_generator import ClientApiMock
from tests.utils.month_utils import month_label
from tests.utils.payload_generator import PayloadGenerator
from tests.utils.request_generator import RequestGenerator


class ObjectGenerator:

    @staticmethod
    def register_fee_configuration(client_key: str = None, payload: dict = None) -> str:
        if client_key is None:
            client_key = str(uuid4())

        if payload is None:
            payload = PayloadGenerator.create_fee_configuration_payload()

        ClientApiMock.GET_client(client_key)

        status, _response = RequestGenerator.POST_fee_configuration(client_key, payload)
        assert status == 201

        return client_key

    @staticmethod
    def record_fee(client_key: str, fee_type: str = None, idempotency_key: str = None) -> dict:
        payload = PayloadGenerator.create_fee_payload(fee_type=fee_type, idempotency_key=idempotency_key)

        status, response = RequestGenerator.POST_fee(client_key, payload)
        assert status == 201

        return response

    @staticmethod
    def close_last_month(fee_types: list = None, payload: dict = None) -> tuple:
        client_key = ObjectGenerator.register_fee_configuration(payload=payload)

        if fee_types is None:
            fee_types = ["transfer"]

        for fee_type in fee_types:
            ObjectGenerator.record_fee(client_key, fee_type=fee_type)

        DbUtils.move_client_dates_back(client_key, 1)

        status, charge = RequestGenerator.POST_charge(client_key, PayloadGenerator.create_charge_payload(month_label(1)))
        assert status == 201

        return client_key, charge
