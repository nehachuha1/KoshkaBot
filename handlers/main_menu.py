from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from keyboards.main_menu_keyboard import main_menu_kb
from keyboards.cancel_button import cancel_kb
from database.database import Database
from services.service import prepare_user_info, prepare_user_orders_text

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

@main_menu_router.callback_query(F.data == 'cancel')
async def process_cancel_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['main_menu_message'],
        reply_markup=main_menu_kb)

@main_menu_router.callback_query(F.data == 'cancel_button')
async def process_cancel_button(callback: CallbackQuery):
    await callback.message.delete()

@main_menu_router.callback_query(F.data == 'cancel_from_shops')
async def process_cancel_to_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['main_menu_message'],
        reply_markup=main_menu_kb)

@main_menu_router.callback_query(F.data == 'my_orders')
async def process_my_orders_user(callback: CallbackQuery, db: Database):
    await callback.answer('')
    
    user_orders_raw = db.get_orders_by_user_id(callback.from_user.id)
    user_order = prepare_user_orders_text(orders=user_orders_raw)

    cancel_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=LEXICON_RU_BUTTONS['CANCEL'],
        callback_data='cancel_button')]])

    await callback.message.answer(
        parse_mode='HTML',
        text=user_order,
        reply_markup=cancel_button
    )

@main_menu_router.message(Command(commands=['info']))
async def process_get_order_info_user(message: Message, db: Database):
    msg_params = message.text.split(' ')[1]
    current_order = db.get_order(order_id=msg_params)

    cancel_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=LEXICON_RU_BUTTONS['CANCEL'],
        callback_data='cancel_button')]])

    if current_order[1] == str(message.from_user.id):
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['USER_ORDER_INFO_MESSAGE'].format(
                order_id=current_order[-1],
                room=current_order[3],
                total_sum=current_order[-3],
                status=current_order[-2]
            ),
            reply_markup=cancel_button
        )
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['WRONG_ORDER_ID_INFO']
        )