import os
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold

from db.orm import BaseAsyncORM
from handlers import start, article

from dotenv import load_dotenv

from parsing_script import get_product_info

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')


async def send_notifications(bot):
    while True:
        async with BaseAsyncORM() as sql:
            subscription_list = await sql.get_subscription()
            for subscription in subscription_list:
                data_info = await get_product_info(subscription.article)
                goods_string = ", \n".join([f"{hbold(key)} - {value}" for key, value in data_info.items()])
                print(subscription.telegram_id)
                await bot.send_message(chat_id=subscription.telegram_id, text=goods_string)
                await sql.set_last_request_time(subscription)
        await asyncio.sleep(int(os.getenv('TIME_PERIOD')))


async def main() -> None:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(start.router, article.router)
    # dp.loop.create_task(send_notifications(bot))
    # await send_notifications(bot)
    asyncio.create_task(send_notifications(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
