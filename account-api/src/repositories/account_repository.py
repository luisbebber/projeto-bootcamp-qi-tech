from decimal import Decimal
from uuid import uuid4

from database import Context
from models import Account, AccountStatus, AccountStatusEvent


class AccountRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, client_key: str, account_data: dict) -> Account:
        account = Account()

        account.account_key = str(uuid4())
        account.client_key = client_key
        account.name = account_data["name"]
        account.document_number = account_data["document_number"]
        account.idempotency_key = account_data["idempotency_key"]

        account.balance = Decimal("0.00")

        self.update_status(account, AccountStatus.ACTIVE)

        self.session.add(account)
        return account

    def update_status(self, account: Account, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        account.status = new_status

        new_status_event = AccountStatusEvent()
        new_status_event.status = new_status

        account.status_events.append(new_status_event)

    def get_by_key(self, client_key: str, account_key: str) -> Account:
        return (
            self.session.query(Account)
            .filter(Account.client_key == client_key)
            .filter(Account.account_key == account_key)
            .first()
        )

    def get_by_key_for_update(self, client_key: str, account_key: str) -> Account:
        return (
            self.session.query(Account)
            .filter(Account.client_key == client_key)
            .filter(Account.account_key == account_key)
            .with_for_update()
            .populate_existing()
            .first()
        )

    def get_by_keys_for_update(self, client_key: str, account_keys: list) -> list:
        return (
            self.session.query(Account)
            .filter(Account.client_key == client_key)
            .filter(Account.account_key.in_(account_keys))
            .order_by(Account.id)
            .with_for_update()
            .populate_existing()
            .all()
        )

    def list_page(self, client_key: str, limit: int, offset: int) -> list:
        return (
            self.session.query(Account)
            .filter(Account.client_key == client_key)
            .order_by(Account.created_at.desc(), Account.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_by_idempotency_key(self, idempotency_key: str) -> Account:
        return (
            self.session.query(Account)
            .filter(Account.idempotency_key == idempotency_key)
            .first()
        )

    def get_active_by_document_number(self, client_key: str, document_number: str) -> Account:
        return (
            self.session.query(Account)
            .join(Account.status)
            .filter(Account.client_key == client_key)
            .filter(Account.document_number == document_number)
            .filter(AccountStatus.enumerator == AccountStatus.ACTIVE)
            .first()
        )

    def get_status(self, enumerator: str) -> AccountStatus:
        return (
            self.session.query(AccountStatus)
            .filter(AccountStatus.enumerator == enumerator)
            .one()
        )
