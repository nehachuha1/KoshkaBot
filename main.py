from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import logging

from config.config import load_env_values, Config
from middlewares.outer.outer_middlewares import MainOuterMiddleware, CheckRegistration
from middlewares.inner.inner_middlewares import AcceptingOrder, HandleOrderBySeller

from handlers.registration_handler import registration_router
from handlers.main_menu import main_menu_router
from handlers.shops_list import shops_list_router
from handlers.shop_interaction import shop_interaction_router
from handlers.seller_interaction import seller_router

logger = logging.getLogger(__name__)

async def main() -> None:
    
    logging.basicConfig(
         level=logging.INFO, format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot...')

    config: Config = load_env_values('.env')
    storage = MemoryStorage()

    bot = Bot(token=config.TgBot.token)
    dp = Dispatcher(storage=storage)
    
    # сюда подключить routers
    dp.include_router(registration_router)
    dp.include_router(main_menu_router)
    dp.include_router(shops_list_router)
    dp.include_router(shop_interaction_router)
    dp.include_router(seller_router)

    # сюда подключить миддлвари
    dp.update.outer_middleware(MainOuterMiddleware())
    registration_router.message.outer_middleware(CheckRegistration())
    shop_interaction_router.callback_query.middleware(AcceptingOrder())
    seller_router.callback_query.middleware(HandleOrderBySeller())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())