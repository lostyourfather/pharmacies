from app.schemas.pharmacies import ProductSchema
from app.models.pharmacies import Product, Price
from app.models.database import database
from sqlalchemy import select


async def get_product(product_header: str = None):
    query = select(Product)
    if product_header:
        query = query.filter_by(header=product_header)
    product = await database.fetch_all(query)
    print(product[0])
    price = await get_price(product[0].product_id)
    print(price)
    return product, price


async def get_price(product_id: int = None):
    print(product_id)
    query = select(Price)
    if product_id:
        query = query.filter_by(product_id=product_id)
    price = await database.fetch_all(query)
    print(price)
    return price
