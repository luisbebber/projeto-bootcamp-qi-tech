from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func
from models.base import Base


class WithdrawalStatus(Base):
    __tablename__ = "withdrawal_status"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    PENDING_CONFIRMATION = "pending_confirmation"
    PENDING_FEE = "pending_fee"
    COMPLETED = "completed"
    REVERSED = "reversed"
