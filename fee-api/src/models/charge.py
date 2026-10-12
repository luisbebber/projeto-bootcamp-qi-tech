from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import ChargeStatus, ClientConfiguration


class Charge(Base):

    __tablename__ = "charge"

    id = Column(BigInteger, primary_key=True)
    charge_key = Column(CHAR(36), nullable=False)
    client_key = Column(CHAR(36), ForeignKey(ClientConfiguration.client_key), nullable=False)
    month = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status_id = Column(Integer, ForeignKey(ChargeStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("charge_key"),
        UniqueConstraint("client_key", "month"),
    )

    status = relationship("ChargeStatus", foreign_keys=[status_id], lazy="selectin")

    status_events = relationship(
        "ChargeStatusEvent",
        back_populates="charge",
        order_by="asc(ChargeStatusEvent.created_at), asc(ChargeStatusEvent.id)",
    )
