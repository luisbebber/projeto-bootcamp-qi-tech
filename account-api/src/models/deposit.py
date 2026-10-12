from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Account, DepositStatus, Transfer


class Deposit(Base):

    __tablename__ = "deposit"

    id = Column(BigInteger, primary_key=True)
    deposit_key = Column(CHAR(36), nullable=False)
    status_id = Column(Integer, ForeignKey(DepositStatus.id), nullable=False)
    account_id = Column(BigInteger, ForeignKey(Account.id), nullable=False)
    transfer_id = Column(BigInteger, ForeignKey(Transfer.id), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("deposit_key"),
        UniqueConstraint("idempotency_key"),
    )

    status = relationship("DepositStatus", foreign_keys=[status_id], lazy="selectin")
    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    transfer = relationship("Transfer", foreign_keys=[transfer_id])

    status_events = relationship(
        "DepositStatusEvent",
        back_populates="deposit",
        order_by="asc(DepositStatusEvent.created_at), asc(DepositStatusEvent.id)",
    )
