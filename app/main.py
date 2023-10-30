from fastapi import FastAPI
from app.models.database import database
from app.routers import pharmacies


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(pharmacies.router)

