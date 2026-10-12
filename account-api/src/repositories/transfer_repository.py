from uuid import uuid4

from database import Context
from models import Account, Transfer


class TransferRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def get_internal_by_idempotency_key(self, idempotency_key: str) -> Transfer:
        return (
            self.session.query(Transfer)
            .filter(Transfer.idempotency_key == idempotency_key)
            .filter(Transfer.origin_account_id.isnot(None))
            .filter(Transfer.destination_account_id.isnot(None))
            .first()
        )

    def create(self, origin_account: Account, destination_account: Account, amount, idempotency_key: str = None) -> Transfer:
        transfer = Transfer()

        transfer.transfer_key = str(uuid4())

        if origin_account is not None:
            transfer.origin_account_id = origin_account.id
        if destination_account is not None:
            transfer.destination_account_id = destination_account.id

        transfer.amount = amount
        transfer.idempotency_key = idempotency_key or str(uuid4())

        self.session.add(transfer)
        return transfer
