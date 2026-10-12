from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from models.base import Base
from models import Account


class Transfer(Base):

    __tablename__ = "transfer"

    id = Column(BigInteger, primary_key=True)
    transfer_key = Column(CHAR(36), nullable=False)
    origin_account_id = Column(BigInteger, ForeignKey(Account.id), nullable=True)
    destination_account_id = Column(BigInteger, ForeignKey(Account.id), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("transfer_key"),
        UniqueConstraint("idempotency_key"),
    )
