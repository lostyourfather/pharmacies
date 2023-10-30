# coding=utf-8
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.sql import func


Base = declarative_base()


class Base(Base):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


def get_engine():
    engine = create_engine("postgresql://postgres:postgres@db:5432/pharmacies", echo=False)
    return engine
