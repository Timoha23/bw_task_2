import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    """
    Модель юзера
    """

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class Audio(Base):
    """
    Модель аудио
    """

    __tablename__ = "audio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
