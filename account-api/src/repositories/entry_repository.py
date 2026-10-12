from uuid import uuid4

from database import Context
from models import Account, Entry, EntryType, Transfer


class EntryRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, account: Account, transfer: Transfer, type_enumerator: str, amount) -> Entry:
        entry = Entry()

        entry.entry_key = str(uuid4())
        entry.type = self.get_type(type_enumerator)
        entry.account_id = account.id
        entry.transfer = transfer
        entry.amount = amount

        account.balance = account.balance + amount
        entry.balance_after = account.balance

        self.session.add(entry)
        return entry

    def list_page(self, account: Account, limit: int, offset: int, from_datetime=None, to_datetime=None) -> list:
        query = self.session.query(Entry).filter(Entry.account_id == account.id)

        if from_datetime is not None:
            query = query.filter(Entry.created_at >= from_datetime)

        if to_datetime is not None:
            query = query.filter(Entry.created_at <= to_datetime)

        return (
            query.order_by(Entry.created_at.desc(), Entry.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_by_transfer_id(self, transfer_id: int) -> Entry:
        return (
            self.session.query(Entry)
            .filter(Entry.transfer_id == transfer_id)
            .first()
        )

    def get_type(self, enumerator: str) -> EntryType:
        return (
            self.session.query(EntryType)
            .filter(EntryType.enumerator == enumerator)
            .one()
        )
