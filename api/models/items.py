from base import Base
from sqlalchemy import Column, INT, VARCHAR, BOOLEAN, DECIMAL


class Items(Base):
    __tablename__ = "items"
    id = Column(INT, primary_key=True, autoincrement=True)
    header = Column(VARCHAR(255), nullable=False)
    price = Column(DECIMAL(2), nullable=False)
    is_prescription = Column(BOOLEAN, nullable=False, default=False)
    img_src = Column(VARCHAR(255), nullable=True)