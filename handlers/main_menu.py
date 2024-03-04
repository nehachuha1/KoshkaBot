from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from lexicon.lexicon import LEXICON_RU
from keyboards.main_menu_keyboard import main_menu_kb
from keyboards.cancel_button import cancel_kb
from database.database import Database
from services.service import prepare_user_info

import logging

main_menu_router = Router()

logger = logging.getLogger(__name__)

@main_menu_router.message(Command(commands='menu'))
async def process_menu_command(message: Message):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['main_menu_message'],
                         reply_markup=main_menu_kb)

@main_menu_router.callback_query(F.data.in_(['check_user_stats']))
async def process_get_user_stats(callback: CallbackQuery, db: Database):
    user_info = db.get_user_info(callback.from_user.id)
    await callback.message.edit_text(
        parse_mode='HTML',
        text=prepare_user_info(user_info=user_info),
        reply_markup=cancel_kb
        )

@main_menu_router.callback_query(F.data.in_(['cancel']))
async def process_cancel_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['main_menu_message'],
        reply_markup=main_menu_kb)