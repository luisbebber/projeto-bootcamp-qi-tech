from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import ClientConfiguration, FeeConfigurationStatus, FeeType


class FeeConfiguration(Base):

    __tablename__ = "fee_configuration"

    id = Column(Integer, primary_key=True)
    fee_configuration_key = Column(CHAR(36), nullable=False)
    client_key = Column(CHAR(36), ForeignKey(ClientConfiguration.client_key), nullable=False)
    fee_type_id = Column(Integer, ForeignKey(FeeType.id), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status_id = Column(Integer, ForeignKey(FeeConfigurationStatus.id), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("fee_configuration_key"),)

    client_configuration = relationship("ClientConfiguration", foreign_keys=[client_key], lazy="selectin")
    fee_type = relationship("FeeType", foreign_keys=[fee_type_id], lazy="selectin")
    status = relationship("FeeConfigurationStatus", foreign_keys=[status_id], lazy="selectin")

    status_events = relationship(
        "FeeConfigurationStatusEvent",
        back_populates="fee_configuration",
        order_by="asc(FeeConfigurationStatusEvent.created_at), asc(FeeConfigurationStatusEvent.id)",
    )
