import requests

from connectors import ClientApiConnector, FeeApiConnector
from controllers.base_controller import BaseController
from dtos import ClientConfigurationDTO
from errors import (
    ClientAlreadyConfigured,
    ClientApiUnavailable,
    ClientNotActive,
    ClientNotFound,
    ClientWithoutFees,
    FeeApiUnavailable,
)
from repositories import ClientConfigurationRepository

ACTIVE_CLIENT_STATUS = "active"


class ClientConfigurationController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.client_api_connector = ClientApiConnector()
        self.fee_api_connector = FeeApiConnector()

    def create(self, client_key: str) -> dict:
        self.logger.debug(f"Configurando a empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is not None:
            raise ClientAlreadyConfigured(client_key)

        self._check_client_is_active(client_key)
        self._check_client_has_fees(client_key)

        client_configuration = self.client_configuration_repository.create(client_key)

        client_configuration_dto = ClientConfigurationDTO.only_obj_key(client_configuration)
        self.session.commit()

        return client_configuration_dto

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

    def _check_client_has_fees(self, client_key: str) -> None:
        try:
            response = self.fee_api_connector.get_fee_configuration(client_key)
        except requests.RequestException:
            self.logger.error(f"A fee-api não respondeu sobre a empresa {client_key}")
            raise FeeApiUnavailable()

        if response.status == 404:
            raise ClientWithoutFees(client_key)

        if response.status != 200:
            self.logger.error(f"A fee-api respondeu {response.status} sobre a empresa {client_key}")
            raise FeeApiUnavailable()
