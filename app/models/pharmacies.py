import sys
sys.path.append('.')
from .base import Base
from sqlalchemy import Column, INT, VARCHAR, BOOLEAN, DECIMAL, TEXT, ForeignKey


class SiteName(Base):
    __tablename__ = 'site_name'
    site_name_id = Column(INT, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(255), nullable=False, unique=True)


class Product(Base):
    __tablename__ = 'product'
    product_id = Column(INT, primary_key=True, autoincrement=True)
    site_name_id = Column(INT, ForeignKey('site_name.site_name_id'))
    header = Column(VARCHAR(255), nullable=False, unique=True)
    description = Column(TEXT, nullable=True)
    is_prescription = Column(BOOLEAN, nullable=False, default=False)
    img_src = Column(VARCHAR(255), nullable=True)
    link = Column(VARCHAR(255), nullable=True)


class Price(Base):
    __tablename__ = "price"
    price_id = Column(INT, primary_key=True, autoincrement=True)
    product_id = Column(INT, ForeignKey('product.product_id'))
    value = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(VARCHAR(3), nullable=True)


