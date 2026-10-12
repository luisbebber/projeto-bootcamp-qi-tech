from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func
from models.base import Base


class EntryType(Base):

    __tablename__ = "entry_type"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    WITHDRAWAL_REVERSED = "withdrawal_reversed"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"
