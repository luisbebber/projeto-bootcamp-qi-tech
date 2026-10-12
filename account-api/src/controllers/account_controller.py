from connectors import FeeApiConnector
from constants import FeeType
from controllers.base_controller import BaseController
from dtos import AccountDTO
from errors import (
    AccountAlreadyClosed,
    AccountHasBalance,
    AccountHasPendingWithdrawal,
    ActiveAccountAlreadyExists,
    ClientNotConfigured,
    FeeApiUnavailable,
    InvalidDocumentNumber,
    NotFoundAccount,
)
from models import AccountStatus, WithdrawalStatus
from repositories import AccountRepository, ClientConfigurationRepository, WithdrawalRepository
from utils.fee_registration import register_fee
from utils.document_number import is_valid_cpf


class AccountController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.withdrawal_repository = WithdrawalRepository(self.context)
        self.fee_api_connector = FeeApiConnector()

    def create(self, client_key: str, account_data: dict) -> dict:
        self.logger.debug(f"Abrindo uma conta na empresa {client_key}")

        document_number = account_data["document_number"]
        idempotency_key = account_data["idempotency_key"]

        existing_account = self.account_repository.get_by_idempotency_key(idempotency_key)
        if existing_account is not None:
            return AccountDTO.only_obj_key_and_status(existing_account)

        if not is_valid_cpf(document_number):
            raise InvalidDocumentNumber(document_number)

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        if self.account_repository.get_active_by_document_number(client_key, document_number) is not None:
            raise ActiveAccountAlreadyExists(document_number)

        account = self.account_repository.create(client_key, account_data)

        fee_registered = register_fee(self.fee_api_connector, self.logger, client_key, FeeType.ACCOUNT_OPENING, idempotency_key)
        if not fee_registered:
            self.session.rollback()
            raise FeeApiUnavailable()

        account_dto = AccountDTO.only_obj_key_and_status(account)
        self.session.commit()

        return account_dto

    def get_by_key(self, client_key: str, account_key: str) -> dict:
        self.logger.debug(f"Buscando a conta {account_key} da empresa {client_key}")

        account = self.account_repository.get_by_key(client_key, account_key)
        if account is None:
            raise NotFoundAccount(account_key)

        return AccountDTO.obj_to_dict(account)

    def get_list(self, client_key: str, limit: int, offset: int) -> dict:
        self.logger.debug(f"Listando as contas da empresa {client_key}")

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        accounts_list = self.account_repository.list_page(client_key, limit, offset)

        is_last_page = True
        if len(accounts_list) > limit:
            is_last_page = False
            accounts_list = accounts_list[:-1]

        return {
            "accounts_list_dto": AccountDTO.list_obj_to_list_dict(accounts_list),
            "is_last_page": is_last_page,
        }

    def close(self, client_key: str, account_key: str) -> dict:
        self.logger.debug(f"Fechando a conta {account_key} da empresa {client_key}")

        account = self.account_repository.get_by_key_for_update(client_key, account_key)
        if account is None:
            raise NotFoundAccount(account_key)

        if account.status.enumerator == AccountStatus.CLOSED:
            raise AccountAlreadyClosed(account_key)

        if account.balance != 0:
            raise AccountHasBalance(account_key)

        pending_withdrawals = self.withdrawal_repository.count_by_account_and_status(
            account, WithdrawalStatus.PENDING_CONFIRMATION
        )
        if pending_withdrawals > 0:
            raise AccountHasPendingWithdrawal(account_key)

        self.account_repository.update_status(account, AccountStatus.CLOSED)

        account_dto = AccountDTO.only_obj_key_and_status(account)
        self.session.commit()

        return account_dto
