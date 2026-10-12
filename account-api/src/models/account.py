from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import AccountStatus, ClientConfiguration


class Account(Base):

    __tablename__ = "account"

    id = Column(BigInteger, primary_key=True)
    account_key = Column(CHAR(36), nullable=False)
    client_key = Column(CHAR(36), ForeignKey(ClientConfiguration.client_key), nullable=False)
    status_id = Column(Integer, ForeignKey(AccountStatus.id), nullable=False)
    name = Column(String(255), nullable=False)
    document_number = Column(CHAR(11), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("account_key"),
        UniqueConstraint("idempotency_key"),
    )

    status = relationship("AccountStatus", foreign_keys=[status_id], lazy="selectin")

    status_events = relationship(
        "AccountStatusEvent",
        back_populates="account",
        order_by="asc(AccountStatusEvent.created_at), asc(AccountStatusEvent.id)",
    )
