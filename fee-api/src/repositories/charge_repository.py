from datetime import date
from decimal import Decimal
from uuid import uuid4

from database import Context
from models import Charge, ChargeStatus, ChargeStatusEvent

TWO_PLACES = Decimal("0.01")


class ChargeRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, client_key: str, month: date, amount: Decimal) -> Charge:
        charge = Charge()

        charge.charge_key = str(uuid4())
        charge.client_key = client_key
        charge.month = month
        charge.amount = amount.quantize(TWO_PLACES)

        self.update_status(charge, ChargeStatus.PENDING_PAYMENT)

        self.session.add(charge)
        return charge

    def update_status(self, charge: Charge, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        charge.status = new_status

        new_status_event = ChargeStatusEvent()
        new_status_event.status = new_status

        charge.status_events.append(new_status_event)

    def get_by_client_key_and_month(self, client_key: str, month: date) -> Charge:
        return (
            self.session.query(Charge)
            .filter(Charge.client_key == client_key)
            .filter(Charge.month == month)
            .first()
        )

    def get_by_key(self, client_key: str, charge_key: str) -> Charge:
        return (
            self.session.query(Charge)
            .filter(Charge.client_key == client_key)
            .filter(Charge.charge_key == charge_key)
            .first()
        )

    def get_by_key_for_update(self, client_key: str, charge_key: str) -> Charge:
        return (
            self.session.query(Charge)
            .filter(Charge.client_key == client_key)
            .filter(Charge.charge_key == charge_key)
            .with_for_update()
            .first()
        )

    def list_page(self, client_key: str, status_enumerator: str, limit: int, offset: int) -> list:
        query = (
            self.session.query(Charge)
            .join(Charge.status)
            .filter(Charge.client_key == client_key)
        )

        if status_enumerator is not None:
            query = query.filter(ChargeStatus.enumerator == status_enumerator)

        return (
            query
            .order_by(Charge.created_at.desc(), Charge.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_status(self, enumerator: str) -> ChargeStatus:
        return (
            self.session.query(ChargeStatus)
            .filter(ChargeStatus.enumerator == enumerator)
            .first()
        )
