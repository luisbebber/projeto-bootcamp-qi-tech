from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Account, EntryType, Transfer


class Entry(Base):

    __tablename__ = "entry"

    id = Column(BigInteger, primary_key=True)
    entry_key = Column(CHAR(36), nullable=False)
    type_id = Column(Integer, ForeignKey(EntryType.id), nullable=False)
    account_id = Column(BigInteger, ForeignKey(Account.id), nullable=False)
    transfer_id = Column(BigInteger, ForeignKey(Transfer.id), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("entry_key"),)

    type = relationship("EntryType", foreign_keys=[type_id], lazy="selectin")
    transfer = relationship("Transfer", foreign_keys=[transfer_id])
