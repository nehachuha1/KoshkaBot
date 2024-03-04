from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from typing import Any, Callable, Awaitable, Dict
import logging

from database.database import Database, CachedDatabase

logger = logging.getLogger(__name__)

class MainOuterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:
        
        db = Database()
        cached_db = CachedDatabase()

        user: User = data['event_from_user']

        data['db'] = db
        data['cached_db'] = cached_db
        data['is_registered'] = db.check_registration(user.id)
        data['is_main_admin'] = db.check_main_admin(user.id)

        result = await handler(event, data)
        return result
    
class CheckRegistration(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:

        cached_db = data['cached_db']
        db = data['db']
        is_registered = data['is_registered']
        
        result = await handler(event, data)
        
        if not is_registered:
            user: User = data['event_from_user']
            new_user_data = cached_db.get_values(str(user.id))
            if new_user_data != None:
                db.register_new_user(new_user_data)
                cached_db.delete_values(str(user.id))
            return
        return result