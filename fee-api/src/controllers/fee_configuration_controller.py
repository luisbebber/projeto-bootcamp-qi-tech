from decimal import Decimal

import requests

from connectors import ClientApiConnector
from controllers.base_controller import BaseController
from dtos import FeeConfigurationDTO
from errors import (
    ClientAlreadyConfigured,
    ClientApiUnavailable,
    ClientNotActive,
    ClientNotConfigured,
    ClientNotFound,
    FeeConfigurationNotChanged,
)
from models import FeeConfigurationStatus, FeeType
from repositories import ClientConfigurationRepository, FeeConfigurationRepository

ACTIVE_CLIENT_STATUS = "active"

FEE_TYPE_FIELDS = {
    FeeType.TRANSFER: "transfer_amount",
    FeeType.ACCOUNT_OPENING: "account_opening_amount",
}


class FeeConfigurationController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.fee_configuration_repository = FeeConfigurationRepository(self.context)
        self.client_api_connector = ClientApiConnector()

    def create(self, client_key: str, fees_data: dict) -> dict:
        self.logger.debug(f"Cadastrando as taxas da empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is not None:
            raise ClientAlreadyConfigured(client_key)

        self._check_client_is_active(client_key)

        client_configuration = self.client_configuration_repository.create(client_key)
        fee_configurations = []
        for fee_type, field in FEE_TYPE_FIELDS.items():
            amount = fees_data[field]
            fee_configuration = self.fee_configuration_repository.create(client_configuration, fee_type, amount)
            fee_configurations.append(fee_configuration)

        fees_dto = FeeConfigurationDTO.client_key_and_fees(client_key, fee_configurations)
        self.session.commit()

        return fees_dto

    def get_by_client_key(self, client_key: str) -> dict:
        self.logger.debug(f"Buscando as taxas ativas da empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        fee_configurations = self.fee_configuration_repository.list_active_by_client_key(client_key)

        return FeeConfigurationDTO.client_key_and_fees(client_key, fee_configurations)

    def update(self, client_key: str, fees_data: dict) -> dict:
        self.logger.debug(f"Trocando as taxas da empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        active_fee_configurations = self.fee_configuration_repository.list_active_by_client_key_for_update(client_key)
        fee_configurations = []
        has_changed = False
        for fee_configuration in active_fee_configurations:
            field = FEE_TYPE_FIELDS[fee_configuration.fee_type.enumerator]

            if field not in fees_data or Decimal(fees_data[field]) == fee_configuration.amount:
                fee_configurations.append(fee_configuration)
                continue

            self.fee_configuration_repository.update_status(fee_configuration, FeeConfigurationStatus.INACTIVE)
            new_fee_configuration = self.fee_configuration_repository.create(
                fee_configuration.client_configuration, fee_configuration.fee_type.enumerator, fees_data[field]
            )
            fee_configurations.append(new_fee_configuration)
            has_changed = True

        if not has_changed:
            raise FeeConfigurationNotChanged(client_key)

        fees_dto = FeeConfigurationDTO.client_key_and_fees(client_key, fee_configurations)
        self.session.commit()

        return fees_dto

    def _check_client_is_active(self, client_key: str) -> None:
        try:
            response = self.client_api_connector.get_client(client_key)
        except requests.RequestException:
            self.logger.error(f"A client-api não respondeu sobre a empresa {client_key}")
            raise ClientApiUnavailable()

        if response.status == 404:
            raise ClientNotFound(client_key)

        if response.status != 200:
            self.logger.error(f"A client-api respondeu {response.status} sobre a empresa {client_key}")
            raise ClientApiUnavailable()

        client_status = response.json["status"]
        if client_status != ACTIVE_CLIENT_STATUS:
            raise ClientNotActive(client_key, client_status)
