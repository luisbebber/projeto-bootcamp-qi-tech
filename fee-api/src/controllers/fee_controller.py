from controllers.base_controller import BaseController
from dtos import FeeDTO
from errors import ClientNotConfigured, NotFoundFee
from repositories import ClientConfigurationRepository, FeeConfigurationRepository, FeeRepository


class FeeController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.fee_configuration_repository = FeeConfigurationRepository(self.context)
        self.fee_repository = FeeRepository(self.context)

    def create(self, client_key: str, fee_data: dict) -> dict:
        self.logger.debug(f"Registrando uma taxa {fee_data['fee_type']} da empresa {client_key}")

        idempotency_key = fee_data["idempotency_key"]

        existing_fee = self.fee_repository.get_by_idempotency_key(idempotency_key)
        if existing_fee is not None:
            return FeeDTO.only_obj_key(existing_fee)

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        fee_configuration = self.fee_configuration_repository.get_active_by_client_key_and_fee_type(
            client_key, fee_data["fee_type"]
        )
        fee = self.fee_repository.create(fee_configuration, idempotency_key)

        fee_dto = FeeDTO.only_obj_key(fee)
        self.session.commit()

        return fee_dto

    def get_by_key(self, client_key: str, fee_key: str) -> dict:
        self.logger.debug(f"Buscando a taxa {fee_key} da empresa {client_key}")

        fee = self.fee_repository.get_by_key(client_key, fee_key)
        if fee is None:
            raise NotFoundFee(fee_key)

        return FeeDTO.obj_to_dict(fee)
