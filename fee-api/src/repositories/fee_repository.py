from datetime import datetime
from uuid import uuid4

from sqlalchemy import func

from database import Context
from models import Charge, ChargeStatus, Fee, FeeConfiguration, FeeType
from utils.time_zone import BRASILIA_OFFSET


class FeeRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, fee_configuration: FeeConfiguration, idempotency_key: str) -> Fee:
        fee = Fee()

        fee.fee_key = str(uuid4())
        fee.idempotency_key = idempotency_key

        fee.client_key = fee_configuration.client_key
        fee.fee_type = fee_configuration.fee_type
        fee.amount = fee_configuration.amount

        self.session.add(fee)
        return fee

    def get_by_idempotency_key(self, idempotency_key: str) -> Fee:
        return (
            self.session.query(Fee)
            .filter(Fee.idempotency_key == idempotency_key)
            .first()
        )

    def get_by_key(self, client_key: str, fee_key: str) -> Fee:
        return (
            self.session.query(Fee)
            .filter(Fee.client_key == client_key)
            .filter(Fee.fee_key == fee_key)
            .first()
        )

    def sum_by_month_and_fee_type(self, client_key: str, from_datetime: datetime, to_datetime: datetime) -> list:
        brasilia_created_at = Fee.created_at - BRASILIA_OFFSET
        month = func.date_trunc("month", brasilia_created_at)
        is_paid = func.coalesce(ChargeStatus.enumerator == ChargeStatus.PAID, False)

        return (
            self.session.query(month, FeeType.enumerator, is_paid, func.sum(Fee.amount))
            .join(FeeType, Fee.fee_type_id == FeeType.id)
            .outerjoin(Charge, Fee.charge_id == Charge.id)
            .outerjoin(ChargeStatus, Charge.status_id == ChargeStatus.id)
            .filter(Fee.client_key == client_key)
            .filter(brasilia_created_at >= from_datetime)
            .filter(brasilia_created_at <= to_datetime)
            .group_by(month, FeeType.id, FeeType.enumerator, is_paid)
            .order_by(month, FeeType.id)
            .all()
        )

    def list_open_by_month(self, client_key: str, month_start: datetime, next_month_start: datetime) -> list:
        brasilia_created_at = Fee.created_at - BRASILIA_OFFSET

        return (
            self.session.query(Fee)
            .filter(Fee.client_key == client_key)
            .filter(Fee.charge_id.is_(None))
            .filter(brasilia_created_at >= month_start)
            .filter(brasilia_created_at < next_month_start)
            .all()
        )

    def attach_to_charge(self, fees: list, charge: Charge) -> None:
        for fee in fees:
            fee.charge = charge
