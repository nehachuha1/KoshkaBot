from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from typing import Any, Callable, Awaitable, Dict
import logging

from database.database import Database, CachedDatabase
# добавление заказа в базу данных + отправка заказа администратору магазина
class AcceptingOrder(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:
        
        
        result = await handler(event, data)
        return result