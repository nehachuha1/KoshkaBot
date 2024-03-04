from aiogram import Bot, Dispatcher

import asyncio
import logging

from config.config import load_env_values, Config
from middlewares.outer.outer_middlewares import MainOuterMiddleware, CheckRegistration

from handlers.registration_handler import registration_router

logger = logging.getLogger(__name__)

async def main() -> None:
    
    logging.basicConfig(
         level=logging.INFO, format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot...')

    config: Config = load_env_values('.env')

    bot = Bot(token=config.TgBot.token)
    dp = Dispatcher()
    
    # сюда подключить routers
    dp.include_router(registration_router)

    # сюда подключить миддлвари
    dp.update.outer_middleware(MainOuterMiddleware())
    registration_router.message.outer_middleware(CheckRegistration())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())