from decimal import Decimal

import requests

from connectors import FeeApiConnector, SpiApiConnector
from constants import FeeType
from controllers.base_controller import BaseController
from dtos import WithdrawalDTO
from errors import (
    AccountClosed,
    FeeApiUnavailable,
    InsufficientBalance,
    NotFoundAccount,
    NotFoundWithdrawal,
    WithdrawalCannotChangeStatus,
    ZeroAmount,
)
from models import AccountStatus, EntryType, WithdrawalStatus
from repositories import AccountRepository, EntryRepository, TransferRepository, WithdrawalRepository
from utils.fee_registration import register_fee

SPI_SENT = "sent"
SPI_REFUSED = "refused"
SPI_UNKNOWN = "unknown"

ALLOWED_TRANSITIONS = {
    WithdrawalStatus.PENDING_CONFIRMATION: (WithdrawalStatus.COMPLETED, WithdrawalStatus.REVERSED),
    WithdrawalStatus.PENDING_FEE: (WithdrawalStatus.COMPLETED,),
}


class WithdrawalController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transfer_repository = TransferRepository(self.context)
        self.withdrawal_repository = WithdrawalRepository(self.context)
        self.entry_repository = EntryRepository(self.context)
        self.spi_api_connector = SpiApiConnector()
        self.fee_api_connector = FeeApiConnector()

    def create(self, client_key: str, account_key: str, withdrawal_data: dict) -> dict:
        self.logger.debug(f"Sacando da conta {account_key} da empresa {client_key}")

        amount = Decimal(withdrawal_data["amount"])
        idempotency_key = withdrawal_data["idempotency_key"]
        receiver_data = withdrawal_data["receiver_data"]

        if amount == 0:
            raise ZeroAmount()

        existing_withdrawal = self.withdrawal_repository.get_by_idempotency_key(idempotency_key)
        if existing_withdrawal is not None:
            return WithdrawalDTO.key_and_status(existing_withdrawal)

        account = self.account_repository.get_by_key_for_update(client_key, account_key)
        if account is None:
            raise NotFoundAccount(account_key)

        if account.status.enumerator == AccountStatus.CLOSED:
            raise AccountClosed(account_key)

        if account.balance < amount:
            raise InsufficientBalance(account_key)

        transfer = self.transfer_repository.create(account, None, amount, idempotency_key)
        withdrawal = self.withdrawal_repository.create(account, transfer, amount, receiver_data, idempotency_key)
        self.entry_repository.create(account, transfer, EntryType.WITHDRAWAL, -amount)

        withdrawal_key = withdrawal.withdrawal_key
        self.session.commit()

        spi_result = self._request_spi(withdrawal_key, amount, receiver_data)

        if spi_result == SPI_SENT:
            self.withdrawal_repository.update_status(withdrawal, WithdrawalStatus.PENDING_FEE)
            self.session.commit()

            fee_registered = register_fee(self.fee_api_connector, self.logger, client_key, FeeType.TRANSFER, idempotency_key)
            if fee_registered:
                self.withdrawal_repository.update_status(withdrawal, WithdrawalStatus.COMPLETED)
                self.session.commit()

        elif spi_result == SPI_REFUSED:
            account = self.account_repository.get_by_key_for_update(client_key, account_key)
            self._reverse(account, withdrawal)
            self.session.commit()


        return WithdrawalDTO.key_and_status(withdrawal)

    def get_list(self, limit: int, offset: int, filters: dict) -> dict:
        self.logger.debug("Listando os saques (lista da equipe)")

        withdrawals_list = self.withdrawal_repository.list_page(filters.get("status"), limit, offset)

        is_last_page = True
        if len(withdrawals_list) > limit:
            is_last_page = False
            withdrawals_list = withdrawals_list[:-1]

        return {
            "withdrawals_list_dto": WithdrawalDTO.list_obj_to_list_dict(withdrawals_list),
            "is_last_page": is_last_page,
        }

    def resolve(self, client_key: str, withdrawal_key: str, new_status: str) -> dict:
        self.logger.debug(f"Resolvendo o saque {withdrawal_key} da empresa {client_key} para {new_status}")

        withdrawal = self.withdrawal_repository.get_by_key(client_key, withdrawal_key)
        if withdrawal is None:
            raise NotFoundWithdrawal(withdrawal_key)

        self._check_transition(withdrawal, new_status)

        if new_status == WithdrawalStatus.REVERSED:
            return self._reverse_pending(client_key, withdrawal)

        return self._confirm(client_key, withdrawal)

    def _reverse_pending(self, client_key: str, withdrawal) -> dict:
        withdrawal_key = withdrawal.withdrawal_key

        account = self.account_repository.get_by_key_for_update(client_key, withdrawal.account.account_key)
        withdrawal = self.withdrawal_repository.get_by_key_for_update(client_key, withdrawal_key)
        self._check_transition(withdrawal, WithdrawalStatus.REVERSED)

        self._reverse(account, withdrawal)

        withdrawal_dto = WithdrawalDTO.key_and_status(withdrawal)
        self.session.commit()

        return withdrawal_dto

    def _confirm(self, client_key: str, withdrawal) -> dict:
        withdrawal_key = withdrawal.withdrawal_key

        if withdrawal.status.enumerator == WithdrawalStatus.PENDING_CONFIRMATION:
            withdrawal = self.withdrawal_repository.get_by_key_for_update(client_key, withdrawal_key)
            self._check_transition(withdrawal, WithdrawalStatus.COMPLETED)

            self.withdrawal_repository.update_status(withdrawal, WithdrawalStatus.PENDING_FEE)
            self.session.commit()

        fee_registered = register_fee(
            self.fee_api_connector, self.logger, client_key, FeeType.TRANSFER, withdrawal.idempotency_key
        )
        if not fee_registered:
            raise FeeApiUnavailable()

        withdrawal = self.withdrawal_repository.get_by_key_for_update(client_key, withdrawal_key)
        self._check_transition(withdrawal, WithdrawalStatus.COMPLETED)

        self.withdrawal_repository.update_status(withdrawal, WithdrawalStatus.COMPLETED)

        withdrawal_dto = WithdrawalDTO.key_and_status(withdrawal)
        self.session.commit()

        return withdrawal_dto

    def _check_transition(self, withdrawal, new_status: str) -> None:
        old_status = withdrawal.status.enumerator

        if new_status not in ALLOWED_TRANSITIONS.get(old_status, ()):
            raise WithdrawalCannotChangeStatus(withdrawal.withdrawal_key, old_status, new_status)

    def _reverse(self, account, withdrawal) -> None:
        self.withdrawal_repository.update_status(withdrawal, WithdrawalStatus.REVERSED)

        reverse_transfer = self.transfer_repository.create(None, account, withdrawal.amount)
        withdrawal.reverse_transfer = reverse_transfer
        self.entry_repository.create(account, reverse_transfer, EntryType.WITHDRAWAL_REVERSED, withdrawal.amount)

    def get_by_key(self, client_key: str, withdrawal_key: str) -> dict:
        self.logger.debug(f"Buscando o saque {withdrawal_key} da empresa {client_key}")

        withdrawal = self.withdrawal_repository.get_by_key(client_key, withdrawal_key)
        if withdrawal is None:
            raise NotFoundWithdrawal(withdrawal_key)

        return WithdrawalDTO.obj_to_dict(withdrawal)

    def _request_spi(self, withdrawal_key: str, amount: Decimal, receiver_data: dict) -> str:
        try:
            response = self.spi_api_connector.post_withdrawal(withdrawal_key, amount, receiver_data)
        except requests.RequestException:
            self.logger.error(f"O serviço do SPI não respondeu ao saque {withdrawal_key}")
            return SPI_UNKNOWN

        if response.status == 201:
            return SPI_SENT

        if response.status == 422:
            return SPI_REFUSED

        self.logger.error(f"O serviço do SPI respondeu {response.status} ao saque {withdrawal_key}")
        return SPI_UNKNOWN
