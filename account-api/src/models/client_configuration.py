from sqlalchemy import CHAR, Column, DateTime, Integer, UniqueConstraint, func
from models.base import Base


class ClientConfiguration(Base):

    __tablename__ = "client_configuration"

    id = Column(Integer, primary_key=True)
    client_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("client_key"),)
