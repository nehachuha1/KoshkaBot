from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, callback_data, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import ShopInteraction, ProductInfoFilter, OrderProductFilter, ProcessingUserOrder
from services.service import prepare_list_products_shop, OrderFillForm
from keyboards.shop_list_keyboard import get_shop_products_kb
from database.database import Database, CachedDatabase

import time

shop_interaction_router = Router()

@shop_interaction_router.callback_query(F.data == 'LEAVE_PRODUCTS_LIST_BUTTON')
async def process_remove_products_list(callback: CallbackQuery):
    await callback.message.delete()

@shop_interaction_router.callback_query(ShopInteraction.filter(F.to_return == True))
async def process_get_main_page_shop(callback: CallbackQuery, callback_data: CallbackData, db: Database):
    products = prepare_list_products_shop(
        db.get_products_of_shop(callback_data.shop_id)
    )

    current_kb = get_shop_products_kb(buttons=products)

    await callback.message.edit_text(text=LEXICON_RU['CHOOSE_PRODUCT'],
                                     reply_markup=current_kb.as_markup())
    
@shop_interaction_router.callback_query(ShopInteraction.filter(F.to_return == False))
async def process_get_main_page_shop(callback: CallbackQuery, callback_data: CallbackData, db: Database):
    products = prepare_list_products_shop(
        db.get_products_of_shop(callback_data.shop_id)
    )

    current_kb = get_shop_products_kb(buttons=products)

    await callback.answer('')

    await callback.message.answer(text=LEXICON_RU['CHOOSE_PRODUCT'],
                                     reply_markup=current_kb.as_markup())


@shop_interaction_router.callback_query(ProductInfoFilter.filter())
async def process_get_product_info(callback: CallbackQuery, callback_data: CallbackData, db: Database):
    current_product = db.get_current_product_info(callback_data.product_id)

    # CHECK BUTTON FOR ORDER
    order_product = InlineKeyboardButton(text=LEXICON_RU_BUTTONS['ORDER_PRODUCT'], callback_data=
                                         OrderProductFilter(shop_id=current_product[0], product_id=current_product[-1]).pack())
    cancel_to_products_list = InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL_TO_PRODUCT_LIST'], callback_data=
                                                   ShopInteraction(shop_id=current_product[0], to_return=True).pack()
        )
    current_kb = InlineKeyboardMarkup(inline_keyboard=[[order_product],[cancel_to_products_list]])

    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['PRODUCT_CARD'].format(
                name=current_product[1],
                description=current_product[2],
                price=current_product[3]),
        reply_markup=current_kb
    )    

@shop_interaction_router.callback_query(OrderProductFilter.filter(), StateFilter(default_state))
async def process_order_product(callback: CallbackQuery, callback_data: CallbackData, db: Database, state: FSMContext):
    current_product = db.get_current_product_info(callback_data.product_id)
    current_user = db.get_user_info(username=callback.from_user.id)

    await state.set_state(OrderFillForm.username)
    await state.update_data(username=current_user[0])
    await state.set_state(OrderFillForm.room)
    await state.update_data(room=current_user[2])
    await state.set_state(OrderFillForm.product_name)
    await state.update_data(product_name=current_product[1])
    await state.set_state(OrderFillForm.price)
    await state.update_data(price=current_product[3])
    await state.set_state(OrderFillForm.shop_id)
    await state.update_data(shop_id=current_product[0])
    await state.set_state(OrderFillForm.product_id)
    await state.update_data(product_id=current_product[-1])
    
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CONFIRM_ORDER'], callback_data=ProcessingUserOrder(accepted=True).pack()),
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['DECLINE_ORDER'], callback_data=ProcessingUserOrder(accepted=False).pack())
        ]
    ])

    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['START_ORDER'].format(
            username=current_user[0],
            room=current_user[2],
            product_name=current_product[1],
            price=current_product[3]
        ),
        reply_markup=buttons
    )
# хэндле на фабрику колбэков для кнопок
@shop_interaction_router.callback_query(ProcessingUserOrder.filter(), ~StateFilter(default_state))
async def process_next_step_order(callback: CallbackQuery, db: Database, cached_db: CachedDatabase, state: FSMContext, callback_data: CallbackData):
    if callback_data.accepted:
        await state.update_data(order_status='Active')
        result = await state.get_data()
        
        cached_db.set_values(f'order:{callback.from_user.id}', result)
        db.register_new_order(
            shop_id=result['shop_id'],
            buyer_id=callback.from_user.id,
            products_ids=result['product_id'],
            room=result['room'],
            totalsum=result['price'],
            status='Active'
        )
        await state.clear()

        await callback.message.edit_text(
            parse_mode='HTML',
            text=LEXICON_RU['ORDER_ACCEPTED'],
        )

    elif not callback_data.accepted:
        await state.clear()

        await callback.message.edit_text(
            parse_mode='HTML',
            text=LEXICON_RU['ORDER_DECLINED'],
        )
    time.sleep(3)
    await callback.message.delete()
