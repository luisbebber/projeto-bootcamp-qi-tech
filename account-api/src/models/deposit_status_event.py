from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Deposit, DepositStatus


class DepositStatusEvent(Base):
    __tablename__ = "deposit_status_event"

    id = Column(BigInteger, primary_key=True)
    deposit_id = Column(BigInteger, ForeignKey(Deposit.id), nullable=False)
    status_id = Column(Integer, ForeignKey(DepositStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    deposit = relationship("Deposit", foreign_keys=[deposit_id], back_populates="status_events", lazy="selectin")
    status = relationship("DepositStatus", foreign_keys=[status_id], lazy="selectin")
