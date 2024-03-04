from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from database.database import CachedDatabase, Database
from keyboards.pagination_keyboard import build_pagination_keyboard
from config.config import DEFAULT_SHOP_PHOTO_ID

import time
from random import randint

shops_list_router = Router()

@shops_list_router.callback_query(F.data.in_(['get_list_of_shops']))
async def process_get_list_of_shops(callback: CallbackQuery, db: Database, cached_db: CachedDatabase):
    await callback.message.edit_text(parse_mode='HTML',
                                  text=LEXICON_RU['loading_shops_1'])
    
    cached_db.set_values(key_value=str(callback.from_user.id), values=1)
    current_shop = db.get_current_shop_info(1)
    time.sleep(1)
    for num in range(2, 6):
        await callback.message.edit_text(text=LEXICON_RU[f'loading_shops_{num}'])
        time.sleep(1)
    await callback.message.delete()
    
    current_kb = build_pagination_keyboard(current_page=1, to_return=2)
    current_kb.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS["CANCEL"], callback_data='cancel_from_shops'))
    current_kb.adjust(3, 1)

    await callback.message.answer_photo(
        parse_mode='HTML',
        photo=current_shop[-1] if current_shop[-1] else DEFAULT_SHOP_PHOTO_ID,
        caption=LEXICON_RU['SHOP_INFO'].format(
            name=current_shop[1],
            description=current_shop[2],
            is_active=current_shop[3],
            admin_id=current_shop[0]
        ),
        reply_markup=current_kb.as_markup()
        )

@shops_list_router.callback_query(F.data.in_(['NEXT_PAGE', 'PREVIOUS_PAGE']))
async def process_prev_next_buttons_keyboard(callback: CallbackQuery, db: Database, cached_db: CachedDatabase, bot: Bot):
    
    flag = False

    cur_page = cached_db.get_values(str(callback.from_user.id))
    if callback.data == 'NEXT_PAGE' and (cur_page < db.get_count_of_shops()):
        cur_page += 1
        current_shop = db.get_current_shop_info(cur_page)
        cached_db.set_values(str(callback.from_user.id), cur_page)
        flag = True
    elif callback.data == 'PREVIOUS_PAGE' and (cur_page > 1):
        cur_page -= 1
        current_shop = db.get_current_shop_info(cur_page)
        cached_db.set_values(str(callback.from_user.id), cur_page)
        flag = True
    
    if flag:
        current_kb = build_pagination_keyboard(current_page=cur_page, to_return=2)
        current_kb.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS["CANCEL"], callback_data='cancel_from_shops'))
        current_kb.adjust(3, 1)

        await bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                parse_mode='HTML',
                media=current_shop[-1] if current_shop[-1] else DEFAULT_SHOP_PHOTO_ID, #сюда айди фотки магазина
                caption=LEXICON_RU['SHOP_INFO'].format(
                                    name=current_shop[1],
                                    description=current_shop[2],
                                    is_active=current_shop[3],
                                    admin_id=current_shop[0])
            ),
            reply_markup=current_kb.as_markup()
        )
    else:
        await callback.answer(LEXICON_RU['error_pagination'])