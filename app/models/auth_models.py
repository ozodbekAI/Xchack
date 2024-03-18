from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import (
    UUID,
    TIMESTAMP,
    BOOLEAN,
    INTEGER,
    TEXT,
    ARRAY,
    JSON,
    FLOAT,
)


from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))
    username = Column(TEXT, unique=True)
    status = Column(ARRAY(INTEGER), nullable=False, default=[])
    attendance = Column(TEXT, default='not defined', nullable=False)
    embeddings = Column(ARRAY(TEXT), default=[], nullable=False)

    group = relationship('Group', back_populates='users')



class Group(Base): 
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    science_name = Column(TEXT, nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.room_id"), nullable=False)
    day_time = Column(TEXT, nullable=False)
    lesson_start_time = Column(TIMESTAMP, nullable=False)
    lesson_end_time = Column(TIMESTAMP, nullable=False)

    users = relationship('User', back_populates='group')

class Room(Base):
    __tablename__ = 'rooms'
    room_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_name = Column(TEXT, nullable=False)
    camera_url = Column(TEXT, nullable=False)



