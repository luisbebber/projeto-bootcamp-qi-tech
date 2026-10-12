from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func
from models.base import Base


class FeeType(Base):

    __tablename__ = "fee_type"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    TRANSFER = "transfer"
    ACCOUNT_OPENING = "account_opening"
