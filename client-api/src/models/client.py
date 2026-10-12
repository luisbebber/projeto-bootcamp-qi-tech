from sqlalchemy import BigInteger, CHAR, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship
from models.base import Base
from models import ClientStatus


class Client(Base):

    __tablename__ = "client"

    id = Column(BigInteger, primary_key=True)
    client_key = Column(CHAR(36), nullable=False)
    status_id = Column(Integer, ForeignKey(ClientStatus.id), nullable=False)
    name = Column(String(255), nullable=False)
    document_number = Column(CHAR(14), nullable=False)
    operation = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("client_key"),)

    status = relationship("ClientStatus", foreign_keys=[status_id], lazy="selectin")

    status_events = relationship(
        "ClientStatusEvent",
        back_populates="client",
        order_by="asc(ClientStatusEvent.created_at), asc(ClientStatusEvent.id)",
    )
