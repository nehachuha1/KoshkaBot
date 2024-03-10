from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.filters import Command, callback_data, StateFilter, and_f
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import ProcessingUserOrder, MyShopPanel, CheckAllowedSymbols, SellerProductInfoFilter
from services.service import ChangeShopPhoto, ChangeShopDescription, ChangeShopName, prepare_list_products_shop_seller
from keyboards.myshop_main_panel import build_myshop_main_kb
from keyboards.shop_list_keyboard import get_shop_products_kb_seller
from database.database import Database, CachedDatabase
from config.config import DEFAULT_SHOP_PHOTO_ID

import time

seller_router = Router()

@seller_router.message(Command(commands=['myshop']))
async def process_activate_seller_mode(message: Message, db: Database, is_seller: bool):
    if is_seller:

        user_shop = db.get_user_shop(message.from_user.id)

        await message.answer(
                parse_mode='HTML',
                text=LEXICON_RU['MY_SHOP_MESSAGE'],
                reply_markup=build_myshop_main_kb(shop_id=user_shop, admin_id=message.from_user.id, db=db)
            )
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ERROR_MYSHOP_COMMAND']
        )

@seller_router.callback_query(F.data == 'cancel_button_shop_interaction')
async def process_cancel_button_shop(callback: CallbackQuery):
    await callback.message.delete()

@seller_router.callback_query(MyShopPanel.filter(F.edit_shop_info == True))
async def process_edit_shop_info(callback: CallbackQuery, callback_data: CallbackData, db: Database, cached_db: CachedDatabase):
    current_shop = db.get_current_shop_info(callback_data.shop_id)
    
    edit_info_button = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT'], callback_data='edit_shop_info_process')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction')
        ]
    ])

    await callback.answer('')
    
    await callback.message.answer_photo(
        parse_mode='HTML',
        photo=current_shop[-1] if current_shop[-1] else DEFAULT_SHOP_PHOTO_ID,
        caption=LEXICON_RU['CURRENT_SHOP_INFO_MESSAGE'].format(
            name=current_shop[1],
            description=current_shop[2],
            is_active=current_shop[-3],
            admin_id=current_shop[0]
        ),
        reply_markup=edit_info_button
    )

@seller_router.callback_query(F.data == 'cancel_editing_shop_info', StateFilter(default_state))
async def process_return_to_edit_shop_info(callback: CallbackQuery):
    await callback.message.delete()

@seller_router.callback_query(F.data == 'edit_shop_info_process', StateFilter(default_state))
async def process_change_shop_info(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:NAME'], callback_data='EDIT_NAME')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:DESCRIPTION'], callback_data='EDIT_DESC')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:PHOTO'], callback_data='EDIT_PHOTO')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_editing_shop_info')
        ]
    ])

    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CHANGE_SHOP_INFO'],
        reply_markup=buttons
    )

@seller_router.message(Command(commands=['cancel_edit']), ~StateFilter(default_state))
async def process_change_shop_info(message: Message, state: FSMContext):
    await state.clear()
    
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:NAME'], callback_data='EDIT_NAME')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:DESCRIPTION'], callback_data='EDIT_DESC')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO:PHOTO'], callback_data='EDIT_PHOTO')
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_editing_shop_info')
        ]
    ])

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CHANGE_SHOP_INFO'],
        reply_markup=buttons
    )
# обработка EDIT_NAME
@seller_router.callback_query(F.data == 'EDIT_NAME', StateFilter(default_state))
async def process_change_shop_name(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['INPUT_NEW_SHOP_NAME']
    )
    await state.set_state(ChangeShopName.shop_name)
    
@seller_router.message(and_f(StateFilter(ChangeShopName.shop_name), CheckAllowedSymbols()))
async def process_change_shop_name(message: Message, db: Database, state: FSMContext):
    current_shop = db.get_user_shop(username=message.from_user.id)
    await state.update_data(name=message.text)

    result = await state.get_data()
    db.change_shop_name(shop_id=current_shop, new_name=result['name'])
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SUCCESSFUL_CHANGING_SHOP_NAME']
    )

# обработка EDIT_DESC
@seller_router.callback_query(F.data == 'EDIT_DESC', StateFilter(default_state))
async def process_change_shop_name(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['INPUT_NEW_SHOP_DESC']
    )
    await state.set_state(ChangeShopDescription.shop_description)
    
@seller_router.message(and_f(StateFilter(ChangeShopDescription.shop_description), CheckAllowedSymbols())) #расширить словарь разрешенных символов
async def process_change_shop_name(message: Message, db: Database, state: FSMContext):
    current_shop = db.get_user_shop(username=message.from_user.id)
    await state.update_data(name=message.text)

    result = await state.get_data()
    db.change_shop_description(shop_id=current_shop, new_description=result['name'])
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SUCCESSFUL_CHANGING_SHOP_DESC']
    )
#обработка EDIT PHOTO
@seller_router.callback_query(F.data == 'EDIT_PHOTO', StateFilter(default_state))
async def process_change_shop_name(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['INPUT_NEW_SHOP_PHOTO']
    )
    await state.set_state(ChangeShopPhoto.shop_photo)
    
@seller_router.message(and_f(StateFilter(ChangeShopPhoto.shop_photo), F.content_type == ContentType.PHOTO)) #расширить словарь разрешенных символов
async def process_change_shop_name(message: Message, db: Database, state: FSMContext):
    current_shop = db.get_user_shop(username=message.from_user.id)
    await state.update_data(photo=message.photo[0].file_id)

    result = await state.get_data()
    db.change_shop_photo(shop_id=current_shop, shop_photo=result['photo'])
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SUCCESSFUL_CHANGING_SHOP_PHOTO']
    )

@seller_router.callback_query(MyShopPanel.filter(F.edit_shop_status==True))
async def process_change_shop_status(callback: CallbackQuery, db: Database):
    current_shop = db.get_current_shop_info(db.get_user_shop(username=callback.from_user.id))
    current_status = current_shop[3]

    if current_status == 'Active':
        db.change_shop_status(shop_id=current_shop[-2], status='Inactive')
    elif current_status == 'Inactive':
        db.change_shop_status(shop_id=current_shop[-2], status='Active')
    
    await callback.answer(
        parse_mode='HTML',
        text=LEXICON_RU['STATUS_CHANGED_SUCCESSFULLY'],
        show_alert=True
    )

@seller_router.callback_query(MyShopPanel.filter(F.edit_products_list==True))
async def process_edit_products_list(callback: CallbackQuery, db: Database):
    current_shop_products = db.get_products_of_shop(shop_id=db.get_user_shop(username=callback.from_user.id))

    products = prepare_list_products_shop_seller(
        products=current_shop_products
    )

    current_kb = get_shop_products_kb_seller(buttons=products)

    await callback.answer('')

    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['EDIT_PRODUCT_MESSAGE'],
        reply_markup=current_kb.as_markup()
    )

@seller_router.callback_query(SellerProductInfoFilter.filter())
async def process_edit_product(callback: CallbackQuery, db: Database):
    await callback.answer('')