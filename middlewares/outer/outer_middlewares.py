from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User

from typing import Any, Callable, Awaitable, Dict
import logging

from database.database import Database, CachedDatabase
from config.config import load_env_values

logger = logging.getLogger(__name__)

class MainOuterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any], 
        ) -> Any:
        
        db = Database()
        cached_db = CachedDatabase()

        user: User = data['event_from_user']

        data['db'] = db
        data['cached_db'] = cached_db
        data['is_registered'] = db.check_registration(user.id)
        if data['is_registered']:
            data['is_seller'] = db.get_user_info(username=str(user.id))[-2]
        data['is_main_admin'] = db.check_main_admin(user.id)
        
        return await handler(event, data)
    
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
                logger.debug(new_user_data)
                db.register_new_user(new_user_data)
                cached_db.delete_values(str(user.id))
                event.answer('Successful registration! Use /menu') #перенести в LEXICON_RU
            return
        return result