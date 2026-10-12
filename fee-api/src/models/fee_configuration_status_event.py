from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import FeeConfiguration, FeeConfigurationStatus


class FeeConfigurationStatusEvent(Base):

    __tablename__ = "fee_configuration_status_event"

    id = Column(BigInteger, primary_key=True)
    fee_configuration_id = Column(Integer, ForeignKey(FeeConfiguration.id), nullable=False)
    status_id = Column(Integer, ForeignKey(FeeConfigurationStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    fee_configuration = relationship(
        "FeeConfiguration", foreign_keys=[fee_configuration_id], back_populates="status_events", lazy="selectin"
    )
    status = relationship("FeeConfigurationStatus", foreign_keys=[status_id], lazy="selectin")
