from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func
from models.base import Base


class ChargeStatus(Base):

    __tablename__ = "charge_status"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
