import asyncio
import logging
import sys, os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from models.base import get_engine
from models.pharmacies import Product, Price, SiteName
from sqlalchemy.orm import Session
from sqlalchemy import select


TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        header, description, is_prescription, img_src, value, currency, site_name = get_data(message.text.lower().strip())
        await bot.send_photo(chat_id=message.chat.id , photo=img_src, caption=f"Header: {header}\nDescription: {description}\nPrescription: {'Yes' if is_prescription else 'No'}\nImage: {img_src}\nPrice: {value}\nCurrency: {currency}\nSite name: {site_name}")
    except Exception as e:
        print(e)
        await message.answer("We didn't find this drug! You can try to find another")


def get_data(request_name):
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Product).filter_by(header=request_name)
        products = session.execute(statement).all()
        statement = select(Price).filter_by(product_id=products[0][0].product_id)
        prices = session.execute(statement).all()
        statement = select(SiteName).filter_by(site_name_id=products[0][0].site_name_id)
        site_name = session.execute(statement).all()
        product = products[0][0]
        price = prices[0][0]
        site_name = site_name[0][0]
        return product.header, product.description, product.is_prescription, product.img_src, price.value, price.currency, site_name.title


async def main() -> None:
    global bot
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
