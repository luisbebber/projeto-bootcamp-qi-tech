from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from models.base import Base
from models import Account, Transfer, WithdrawalStatus


class Withdrawal(Base):

    __tablename__ = "withdrawal"

    id = Column(BigInteger, primary_key=True)
    withdrawal_key = Column(CHAR(36), nullable=False)
    status_id = Column(Integer, ForeignKey(WithdrawalStatus.id), nullable=False)
    account_id = Column(BigInteger, ForeignKey(Account.id), nullable=False)
    transfer_id = Column(BigInteger, ForeignKey(Transfer.id), nullable=False)
    reverse_transfer_id = Column(BigInteger, ForeignKey(Transfer.id), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    receiver_data = Column(JSONB, nullable=False)
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("withdrawal_key"),
        UniqueConstraint("idempotency_key"),
    )

    status = relationship("WithdrawalStatus", foreign_keys=[status_id], lazy="selectin")
    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    transfer = relationship("Transfer", foreign_keys=[transfer_id])
    reverse_transfer = relationship("Transfer", foreign_keys=[reverse_transfer_id])

    status_events = relationship(
        "WithdrawalStatusEvent",
        back_populates="withdrawal",
        order_by="asc(WithdrawalStatusEvent.created_at), asc(WithdrawalStatusEvent.id)",
    )
