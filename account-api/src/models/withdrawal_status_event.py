from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Withdrawal, WithdrawalStatus


class WithdrawalStatusEvent(Base):
    __tablename__ = "withdrawal_status_event"

    id = Column(BigInteger, primary_key=True)
    withdrawal_id = Column(BigInteger, ForeignKey(Withdrawal.id), nullable=False)
    status_id = Column(Integer, ForeignKey(WithdrawalStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    withdrawal = relationship("Withdrawal", foreign_keys=[withdrawal_id], back_populates="status_events", lazy="selectin")
    status = relationship("WithdrawalStatus", foreign_keys=[status_id], lazy="selectin")
