from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import Charge, ChargeStatus


class ChargeStatusEvent(Base):

    __tablename__ = "charge_status_event"

    id = Column(BigInteger, primary_key=True)
    charge_id = Column(BigInteger, ForeignKey(Charge.id), nullable=False)
    status_id = Column(Integer, ForeignKey(ChargeStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    charge = relationship("Charge", foreign_keys=[charge_id], back_populates="status_events", lazy="selectin")
    status = relationship("ChargeStatus", foreign_keys=[status_id], lazy="selectin")
