from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Charge, ClientConfiguration, FeeType


class Fee(Base):

    __tablename__ = "fee"

    id = Column(BigInteger, primary_key=True)
    fee_key = Column(CHAR(36), nullable=False)
    client_key = Column(CHAR(36), ForeignKey(ClientConfiguration.client_key), nullable=False)
    fee_type_id = Column(Integer, ForeignKey(FeeType.id), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    charge_id = Column(BigInteger, ForeignKey(Charge.id), nullable=True)
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("fee_key"),
        UniqueConstraint("idempotency_key"),
    )

    fee_type = relationship("FeeType", foreign_keys=[fee_type_id], lazy="selectin")
    charge = relationship("Charge", foreign_keys=[charge_id], lazy="selectin")
