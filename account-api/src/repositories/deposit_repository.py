from uuid import uuid4

from database import Context
from models import Account, Deposit, DepositStatus, DepositStatusEvent, Transfer


class DepositRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, account: Account, transfer: Transfer, amount, idempotency_key: str) -> Deposit:
        deposit = Deposit()

        deposit.deposit_key = str(uuid4())
        deposit.account_id = account.id
        deposit.transfer = transfer
        deposit.amount = amount
        deposit.idempotency_key = idempotency_key

        self.update_status(deposit, DepositStatus.PENDING_FEE)

        self.session.add(deposit)
        return deposit

    def update_status(self, deposit: Deposit, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        deposit.status = new_status

        new_status_event = DepositStatusEvent()
        new_status_event.status = new_status

        deposit.status_events.append(new_status_event)

    def list_page(self, status_enumerator: str, limit: int, offset: int) -> list:
        query = self.session.query(Deposit)

        if status_enumerator is not None:
            query = query.join(Deposit.status).filter(DepositStatus.enumerator == status_enumerator)

        return (
            query.order_by(Deposit.created_at.desc(), Deposit.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_by_key(self, client_key: str, deposit_key: str) -> Deposit:
        return (
            self.session.query(Deposit)
            .join(Account, Account.id == Deposit.account_id)
            .filter(Account.client_key == client_key)
            .filter(Deposit.deposit_key == deposit_key)
            .first()
        )

    def get_by_key_for_update(self, client_key: str, deposit_key: str) -> Deposit:
        return (
            self.session.query(Deposit)
            .join(Account, Account.id == Deposit.account_id)
            .filter(Account.client_key == client_key)
            .filter(Deposit.deposit_key == deposit_key)
            .with_for_update(of=Deposit)
            .populate_existing()
            .first()
        )

    def get_by_idempotency_key(self, idempotency_key: str) -> Deposit:
        return (
            self.session.query(Deposit)
            .filter(Deposit.idempotency_key == idempotency_key)
            .first()
        )

    def get_status(self, enumerator: str) -> DepositStatus:
        return (
            self.session.query(DepositStatus)
            .filter(DepositStatus.enumerator == enumerator)
            .one()
        )
