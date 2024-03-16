from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User

from typing import Any, Callable, Awaitable, Dict
from services.service import send_notification_to_seller, send_notification_to_buyer
import logging

from database.database import Database, CachedDatabase

class AcceptingOrder(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:
        
        cached_db: CachedDatabase = data['cached_db']
        db: Database = data['db']
        
        result = await handler(event, data)

        user: User = data['event_from_user']
        bot: Bot = data['bot']

        current_order = cached_db.get_values(key_value=f'order:{user.id}')
        
        if current_order:
            if current_order['order_status'] == 'Active':
                await send_notification_to_seller(
                    shop_id=current_order['shop_id'],
                    bot=bot,
                    db=db
                )
                cached_db.delete_values(f'order:{user.id}')
        return result
    
class HandleOrderBySeller(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:
        
        cached_db: CachedDatabase = data['cached_db']
        db: Database = data['db']
        
        result = await handler(event, data)

        user: User = data['event_from_user']
        bot: Bot = data['bot']

        current_order = cached_db.get_values(key_value=f'handle_order:id{user.id}')
        
        if current_order:
            if current_order[0] == True:
                await send_notification_to_buyer(
                    order_id=current_order[1],
                    bot=bot,
                    db=db,
                    accepted=True
                )
                cached_db.delete_values(f'handle_order:id{user.id}')
            elif current_order[0] == False:
                await send_notification_to_buyer(
                    order_id=current_order[1],
                    bot=bot,
                    db=db,
                    accepted=False
                )
        return result