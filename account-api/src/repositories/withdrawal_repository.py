from sqlalchemy import func
from uuid import uuid4

from database import Context
from models import Account, Transfer, Withdrawal, WithdrawalStatus, WithdrawalStatusEvent


class WithdrawalRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, account: Account, transfer: Transfer, amount, receiver_data: dict, idempotency_key: str) -> Withdrawal:
        withdrawal = Withdrawal()

        withdrawal.withdrawal_key = str(uuid4())
        withdrawal.account_id = account.id
        withdrawal.transfer = transfer
        withdrawal.amount = amount
        withdrawal.receiver_data = receiver_data
        withdrawal.idempotency_key = idempotency_key

        self.update_status(withdrawal, WithdrawalStatus.PENDING_CONFIRMATION)

        self.session.add(withdrawal)
        return withdrawal

    def update_status(self, withdrawal: Withdrawal, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        withdrawal.status = new_status

        new_status_event = WithdrawalStatusEvent()
        new_status_event.status = new_status

        withdrawal.status_events.append(new_status_event)

    def get_by_key(self, client_key: str, withdrawal_key: str) -> Withdrawal:
        return (
            self.session.query(Withdrawal)
            .join(Account, Account.id == Withdrawal.account_id)
            .filter(Account.client_key == client_key)
            .filter(Withdrawal.withdrawal_key == withdrawal_key)
            .first()
        )

    def list_page(self, status_enumerator: str, limit: int, offset: int) -> list:
        query = self.session.query(Withdrawal)

        if status_enumerator is not None:
            query = query.join(Withdrawal.status).filter(WithdrawalStatus.enumerator == status_enumerator)

        return (
            query.order_by(Withdrawal.created_at.desc(), Withdrawal.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_by_key_for_update(self, client_key: str, withdrawal_key: str) -> Withdrawal:
        return (
            self.session.query(Withdrawal)
            .join(Account, Account.id == Withdrawal.account_id)
            .filter(Account.client_key == client_key)
            .filter(Withdrawal.withdrawal_key == withdrawal_key)
            .with_for_update(of=Withdrawal)
            .populate_existing()
            .first()
        )

    def get_by_idempotency_key(self, idempotency_key: str) -> Withdrawal:
        return (
            self.session.query(Withdrawal)
            .filter(Withdrawal.idempotency_key == idempotency_key)
            .first()
        )

    def count_by_account_and_status(self, account: Account, status_enumerator: str) -> int:
        return (
            self.session.query(func.count(Withdrawal.id))
            .join(Withdrawal.status)
            .filter(Withdrawal.account_id == account.id)
            .filter(WithdrawalStatus.enumerator == status_enumerator)
            .scalar()
        )

    def get_status(self, enumerator: str) -> WithdrawalStatus:
        return (
            self.session.query(WithdrawalStatus)
            .filter(WithdrawalStatus.enumerator == enumerator)
            .one()
        )
