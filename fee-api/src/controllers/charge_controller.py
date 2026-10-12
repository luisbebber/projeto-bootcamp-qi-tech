from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from controllers.base_controller import BaseController
from dtos import ChargeDTO
from errors import ChargeNotPending, ClientNotConfigured, MonthAlreadyClosed, MonthBeforeConfiguration, MonthNotEnded, NotFoundCharge
from models import ChargeStatus
from repositories import ChargeRepository, ClientConfigurationRepository, FeeRepository
from utils.time_zone import BRASILIA_OFFSET

BRASILIA = timezone(-BRASILIA_OFFSET)


class ChargeController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.fee_repository = FeeRepository(self.context)
        self.charge_repository = ChargeRepository(self.context)

    def create(self, client_key: str, charge_data: dict) -> dict:
        self.logger.debug(f"Fechando o mês {charge_data['month']} da empresa {client_key}")

        month = date.fromisoformat(f"{charge_data['month']}-01")

        client_configuration = self.client_configuration_repository.get_by_client_key(client_key)
        if client_configuration is None:
            raise ClientNotConfigured(client_key)

        if self.charge_repository.get_by_client_key_and_month(client_key, month) is not None:
            raise MonthAlreadyClosed(charge_data["month"], client_key)

        current_month = datetime.now(BRASILIA).date().replace(day=1)
        if month >= current_month:
            raise MonthNotEnded(charge_data["month"])

        configuration_month = (client_configuration.created_at - BRASILIA_OFFSET).date().replace(day=1)
        if month < configuration_month:
            raise MonthBeforeConfiguration(charge_data["month"], client_key)

        next_month = (month + timedelta(days=31)).replace(day=1)
        fees = self.fee_repository.list_open_by_month(
            client_key,
            datetime.combine(month, time.min),
            datetime.combine(next_month, time.min),
        )

        amount = Decimal("0.00")
        for fee in fees:
            amount += fee.amount

        charge = self.charge_repository.create(client_key, month, amount)
        self.fee_repository.attach_to_charge(fees, charge)

        charge_dto = ChargeDTO.obj_to_dict(charge)
        self.session.commit()

        return charge_dto

    def update(self, client_key: str, charge_key: str, charge_data: dict) -> dict:
        self.logger.debug(f"Marcando a cobrança {charge_key} da empresa {client_key} como {charge_data['status']}")

        charge = self.charge_repository.get_by_key_for_update(client_key, charge_key)
        if charge is None:
            raise NotFoundCharge(charge_key)

        if charge.status.enumerator != ChargeStatus.PENDING_PAYMENT:
            raise ChargeNotPending(charge_key, charge.status.enumerator)

        self.charge_repository.update_status(charge, charge_data["status"])
        charge_dto = ChargeDTO.key_and_status(charge)
        self.session.commit()

        return charge_dto

    def get_by_key(self, client_key: str, charge_key: str) -> dict:
        self.logger.debug(f"Buscando a cobrança {charge_key} da empresa {client_key}")

        charge = self.charge_repository.get_by_key(client_key, charge_key)
        if charge is None:
            raise NotFoundCharge(charge_key)

        return ChargeDTO.obj_to_simplified_dict(charge)

    def get_list(self, client_key: str, limit: int, offset: int, filters: dict) -> dict:
        self.logger.debug(f"Listando as cobranças da empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        charges = self.charge_repository.list_page(client_key, filters.get("status"), limit, offset)

        is_last_page = True
        if len(charges) > limit:
            is_last_page = False
            charges = charges[:-1]

        return {
            "charges_list_dto": ChargeDTO.list_obj_to_list_dict(charges),
            "is_last_page": is_last_page,
        }
