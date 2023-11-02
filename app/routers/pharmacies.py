from fastapi import APIRouter, HTTPException, status, Response
from app.utils.pharmacies import get_product
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/product", tags=["product"])


@router.get("/")
async def get_orders_by_filters(product_header: str = None):
    db_products, db_prices, db_site_name = await get_product(product_header=product_header)
    if not db_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Can`t find products")
    response = {
        "product_id": db_products[0].product_id,
        "header": db_products[0].header,
        "site_name": db_site_name[0].title,
        "description": db_products[0].description,
        "is_prescription": db_products[0].is_prescription,
        "img_src": db_products[0].img_src,
        "prices": []
    }
    for db_price in db_prices:
        response["prices"].append(
            {
                "value": float(db_price.value),
                "currency": db_price.currency
            }
        )
    print(response)
    return JSONResponse(content=response)
