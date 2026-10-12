from decimal import Decimal

from controllers.base_controller import BaseController
from dtos import TransferDTO
from errors import AccountClosed, InsufficientBalance, NotFoundAccount, SameAccountTransfer, ZeroAmount
from models import AccountStatus, EntryType
from repositories import AccountRepository, EntryRepository, TransferRepository


class TransferController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transfer_repository = TransferRepository(self.context)
        self.entry_repository = EntryRepository(self.context)

    def create(self, client_key: str, transfer_data: dict) -> dict:
        self.logger.debug(f"Transferindo na empresa {client_key}")

        origin_account_key = transfer_data["origin_account_key"]
        destination_account_key = transfer_data["destination_account_key"]
        amount = Decimal(transfer_data["amount"])
        idempotency_key = transfer_data["idempotency_key"]

        if amount == 0:
            raise ZeroAmount()

        if origin_account_key == destination_account_key:
            raise SameAccountTransfer(origin_account_key)

        existing_transfer = self.transfer_repository.get_internal_by_idempotency_key(idempotency_key)
        if existing_transfer is not None:
            return TransferDTO.only_obj_key(existing_transfer)

        locked_accounts = self.account_repository.get_by_keys_for_update(
            client_key, [origin_account_key, destination_account_key]
        )
        accounts_by_key = {}
        for locked_account in locked_accounts:
            accounts_by_key[locked_account.account_key] = locked_account

        origin_account = accounts_by_key.get(origin_account_key)
        if origin_account is None:
            raise NotFoundAccount(origin_account_key)

        destination_account = accounts_by_key.get(destination_account_key)
        if destination_account is None:
            raise NotFoundAccount(destination_account_key)

        for account in (origin_account, destination_account):
            if account.status.enumerator == AccountStatus.CLOSED:
                raise AccountClosed(account.account_key)

        if origin_account.balance < amount:
            raise InsufficientBalance(origin_account_key)

        transfer = self.transfer_repository.create(origin_account, destination_account, amount, idempotency_key)
        self.entry_repository.create(origin_account, transfer, EntryType.TRANSFER_OUT, -amount)
        self.entry_repository.create(destination_account, transfer, EntryType.TRANSFER_IN, amount)

        transfer_dto = TransferDTO.only_obj_key(transfer)
        self.session.commit()

        return transfer_dto
