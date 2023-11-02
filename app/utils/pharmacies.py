from app.models.pharmacies import Product, Price, SiteName
from app.models.database import database
from sqlalchemy import select


async def get_product(product_header: str = None):
    query = select(Product)
    if product_header:
        query = query.filter_by(header=product_header)
    product = await database.fetch_all(query)
    print(product[0])
    price = await get_price(product[0].product_id)
    site_name = await get_site_name(product[0].site_name_id)
    print(price)
    return product, price, site_name


async def get_price(product_id: int = None):
    print(product_id)
    query = select(Price)
    if product_id:
        query = query.filter_by(product_id=product_id)
    price = await database.fetch_all(query)
    print(price)
    return price


async def get_site_name(site_name_id: int = None):
    query = select(SiteName)
    if site_name_id:
        query = query.filter_by(site_name_id=site_name_id)
    site_name = await database.fetch_all(query)
    return site_name
