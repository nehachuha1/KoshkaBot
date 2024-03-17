from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from keyboards.main_menu_keyboard import main_menu_kb
# from keyboards.cancel_button import cancel_kb
from database.database import Database
from filters.filters import CheckAllowedSymbolsDigit, CompleteOrder
from services.service import prepare_user_info, prepare_user_orders_text, ChangeUserRoom

import logging

main_menu_router = Router()

logger = logging.getLogger(__name__)

@main_menu_router.message(Command(commands='menu'))
async def process_menu_command(message: Message):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['main_menu_message'],
                         reply_markup=main_menu_kb)

@main_menu_router.callback_query(F.data == 'about_bot_info')
async def process_send_about_bot_info(callback: CallbackQuery):
    
    await callback.answer('')

    cancel_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=LEXICON_RU_BUTTONS['CANCEL'],
        callback_data='cancel_button')]])
    
    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['ABOUT_BOT'],
        reply_markup=cancel_button
    )

@main_menu_router.callback_query(F.data.in_(['check_user_stats']))
async def process_get_user_stats(callback: CallbackQuery, db: Database):
    user_info = db.get_user_info(callback.from_user.id)

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['USER_EDIT_ROOM_BUTTON'], callback_data='USER_EDIT_ROOM_BUTTON'),
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS["CANCEL"], callback_data='cancel')
        ]
    ])

    await callback.message.edit_text(
        parse_mode='HTML',
        text=prepare_user_info(user_info=user_info),
        reply_markup=cancel_kb
        )

@main_menu_router.callback_query(F.data == 'USER_EDIT_ROOM_BUTTON', StateFilter(default_state))
async def process_change_user_room(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeUserRoom.user_room)

    await callback.answer('')

    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SEND_NEW_ROOM_NUMBER_MESSAGE']
    )

@main_menu_router.message(StateFilter(ChangeUserRoom.user_room), CheckAllowedSymbolsDigit())
async def process_chande_user_room_successfully(message: Message, state: FSMContext, db: Database):
    await state.update_data(new_room=message.text)

    result = await state.get_data()
    db.change_user_room(
        user_id=message.from_user.id,
        room=result['new_room']
    )

    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CHANGED_ROOM_NUM_SUCCESSFULLY']
    )

@main_menu_router.message(~StateFilter(default_state), Command(commands=['cancel_change']))
async def process_chande_user_room_successfully(message: Message, state: FSMContext, db: Database):
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CANCEl_EDITING_USER_ROOM']
    )

@main_menu_router.message(StateFilter(ChangeUserRoom.user_room), ~CheckAllowedSymbolsDigit())
async def process_wrong_room_num_message(message: Message, state: FSMContext):
    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['WRONG_ROOM_NUM']
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

    await message.delete()

    if current_order[-2] == 'In Progress':
        order_interaction_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU_BUTTONS['COMPLETE_ORDER'], callback_data=CompleteOrder(
                    user_id=message.from_user.id,
                    order_id=int(msg_params)
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button')
            ]
        ])
    else:
         order_interaction_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button')
            ]
        ])

    if current_order[1] == str(message.from_user.id):
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['USER_ORDER_INFO_MESSAGE'].format(
                order_id=current_order[-1],
                room=current_order[3],
                total_sum=current_order[-3],
                status=current_order[-2]
            ),
            reply_markup=order_interaction_markup
        )
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['WRONG_ORDER_ID_INFO']
        )

@main_menu_router.callback_query(CompleteOrder.filter(F.is_seller == False))
async def process_complete_order_by_user(callback: CallbackQuery, callback_data: CallbackData, db: Database):
    current_order = db.get_order(order_id=callback_data.order_id)

    if str(current_order[1]) == str(callback_data.user_id):
        await callback.message.delete()

        db.complete_order(order_id=callback_data.order_id)

        await callback.message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ORDER_COMPLETED_BY_USER'].format(order_id=callback_data.order_id)
        )
    else:
        await callback.message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ERROR_BY_CLOSING_ORDER_BY_USER']
        )