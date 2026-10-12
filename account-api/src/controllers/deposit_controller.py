from decimal import Decimal

from connectors import FeeApiConnector
from constants import FeeType
from controllers.base_controller import BaseController
from dtos import DepositDTO
from errors import AccountClosed, DepositNotPendingFee, FeeApiUnavailable, NotFoundAccount, NotFoundDeposit, ZeroAmount
from models import AccountStatus, DepositStatus, EntryType
from repositories import AccountRepository, DepositRepository, EntryRepository, TransferRepository
from utils.fee_registration import register_fee


class DepositController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transfer_repository = TransferRepository(self.context)
        self.deposit_repository = DepositRepository(self.context)
        self.entry_repository = EntryRepository(self.context)
        self.fee_api_connector = FeeApiConnector()

    def create(self, client_key: str, account_key: str, deposit_data: dict) -> dict:
        self.logger.debug(f"Depositando na conta {account_key} da empresa {client_key}")

        amount = Decimal(deposit_data["amount"])
        idempotency_key = deposit_data["idempotency_key"]

        if amount == 0:
            raise ZeroAmount()

        existing_deposit = self.deposit_repository.get_by_idempotency_key(idempotency_key)
        if existing_deposit is not None:
            existing_entry = self.entry_repository.get_by_transfer_id(existing_deposit.transfer_id)
            return DepositDTO.key_and_balance_after(existing_deposit, existing_entry.balance_after)

        account = self.account_repository.get_by_key_for_update(client_key, account_key)
        if account is None:
            raise NotFoundAccount(account_key)

        if account.status.enumerator == AccountStatus.CLOSED:
            raise AccountClosed(account_key)

        transfer = self.transfer_repository.create(None, account, amount, idempotency_key)
        deposit = self.deposit_repository.create(account, transfer, amount, idempotency_key)
        entry = self.entry_repository.create(account, transfer, EntryType.DEPOSIT, amount)

        deposit_dto = DepositDTO.key_and_balance_after(deposit, entry.balance_after)
        self.session.commit()

        fee_registered = register_fee(self.fee_api_connector, self.logger, client_key, FeeType.TRANSFER, idempotency_key)

        if fee_registered:
            self.deposit_repository.update_status(deposit, DepositStatus.COMPLETED)
            self.session.commit()

        return deposit_dto

    def get_list(self, limit: int, offset: int, filters: dict) -> dict:
        self.logger.debug("Listando os depósitos (lista da equipe)")

        deposits_list = self.deposit_repository.list_page(filters.get("status"), limit, offset)

        is_last_page = True
        if len(deposits_list) > limit:
            is_last_page = False
            deposits_list = deposits_list[:-1]

        return {
            "deposits_list_dto": DepositDTO.list_obj_to_list_dict(deposits_list),
            "is_last_page": is_last_page,
        }

    def complete(self, client_key: str, deposit_key: str) -> dict:
        self.logger.debug(f"Completando o depósito {deposit_key} da empresa {client_key}")

        deposit = self.deposit_repository.get_by_key(client_key, deposit_key)
        if deposit is None:
            raise NotFoundDeposit(deposit_key)

        if deposit.status.enumerator != DepositStatus.PENDING_FEE:
            raise DepositNotPendingFee(deposit_key, deposit.status.enumerator)

        fee_registered = register_fee(
            self.fee_api_connector, self.logger, client_key, FeeType.TRANSFER, deposit.idempotency_key
        )
        if not fee_registered:
            raise FeeApiUnavailable()

        deposit = self.deposit_repository.get_by_key_for_update(client_key, deposit_key)
        if deposit.status.enumerator != DepositStatus.PENDING_FEE:
            raise DepositNotPendingFee(deposit_key, deposit.status.enumerator)

        self.deposit_repository.update_status(deposit, DepositStatus.COMPLETED)

        deposit_dto = DepositDTO.key_and_status(deposit)
        self.session.commit()

        return deposit_dto
