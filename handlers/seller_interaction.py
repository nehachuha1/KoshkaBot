from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.filters import Command, callback_data, StateFilter, and_f
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import MyShopPanel, CheckAllowedSymbols, CheckAllowedSymbolsDigit, ProductCardInteraction, DeletingProductCard, HandleOrderBySeller, CompleteOrder, CreateNewProduct
from services.service import ChangeShopPhoto, ChangeShopDescription, ChangeShopName, prepare_list_products_shop_seller, prepare_shop_statistics, CurrentProduct, DeleteProductCardConfirm, active_order_keyboard, prepare_text_orders,\
CreateNewProductFSM
from keyboards.myshop_main_panel import build_myshop_main_kb
# from keyboards.shop_list_keyboard import get_shop_products_kb_seller
from keyboards.orders_keyboard import prepare_orders_for_seller
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

    current_message = LEXICON_RU['EDIT_PRODUCT_MESSAGE'] + products
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['ADD_NEW_PRODUCT'], callback_data=CreateNewProduct(
                admin_id=callback.from_user.id,
                shop_id=db.get_user_shop(username=callback.from_user.id)
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_editing_product_kb')
        ]
    ])

    await callback.answer('')

    await callback.message.answer(
        parse_mode='HTML',
        text=current_message,
        reply_markup=cancel_kb
    )

@seller_router.callback_query(CreateNewProduct.filter(), StateFilter(default_state))
async def process_create_new_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    
    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CREATE_PRODUCT_NAME']
    )

    await state.set_state(CreateNewProductFSM.name)

@seller_router.message(StateFilter(CreateNewProductFSM.name), CheckAllowedSymbols())
async def process_create_new_product_2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CREATE_PRODUCT_DESCRIPTION']
    )

    await state.set_state(CreateNewProductFSM.description)

@seller_router.message(StateFilter(CreateNewProductFSM.description), CheckAllowedSymbols())
async def process_create_new_product_3(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CREATE_PRODUCT_PRICE']
    )

    await state.set_state(CreateNewProductFSM.price)

@seller_router.message(StateFilter(CreateNewProductFSM.price), CheckAllowedSymbolsDigit())
async def process_create_new_product_final(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    
    result = await state.get_data()
    shop_id = db.get_user_shop(username=message.from_user.id)
    
    db.create_new_product(
        shop_id=shop_id,
        name=result['name'],
        description=result['description'],
        price=result['price']
        )
    
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SUCCESSFULLY_CREATED_NEW_PRODUCT']
    )

@seller_router.message(Command(commands=['cancel_create_product']), ~StateFilter(default_state))
async def process_create_product_seller_cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CANCEL_CREATE_PRODUCT'],
        show_alert=True
    )

@seller_router.message(StateFilter(CreateNewProductFSM.price), ~CheckAllowedSymbolsDigit())
async def process_wrong_input_symbols(message: Message):
    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['WRONG_INPUT_SYMBOLS']
    )

@seller_router.callback_query(F.data == 'cancel_editing_product_kb')
async def process_cancel_editing_product_kb(callback: CallbackQuery):
    await callback.message.delete()

@seller_router.callback_query(F.data == 'LEAVE_PRODUCT_EDIT')
async def process_edit_products_list(callback: CallbackQuery, db: Database):
    current_shop_products = db.get_products_of_shop(shop_id=db.get_user_shop(username=callback.from_user.id))

    products = prepare_list_products_shop_seller(
        products=current_shop_products
    )

    current_message = LEXICON_RU['EDIT_PRODUCT_MESSAGE'] + products
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_editing_product_kb')
        ]
    ])

    await callback.answer('')

    await callback.message.edit_text(
        parse_mode='HTML',
        text=current_message,
        reply_markup=cancel_kb
    )

@seller_router.message(Command(commands=['product']))
async def process_edit_product(message: Message, db: Database):
    msg_params = message.text.split(' ')[1]

    current_product = db.get_current_product_info(product_id=msg_params)

    if current_product:
        if str(db.get_current_shop_info(current_shop=current_product[0])[0]) == str(message.from_user.id):
            current_kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_PRODUCT'], callback_data=ProductCardInteraction(
                        shop_id=db.get_current_product_info(product_id=msg_params)[0],
                        product_id=msg_params,
                        edit_product = True,
                        delete_product = False).pack()
                        )
                ],
                [
                    InlineKeyboardButton(text=LEXICON_RU_BUTTONS['DELETE_PRODUCT'], callback_data=ProductCardInteraction(
                        shop_id=db.get_current_product_info(product_id=msg_params)[0],
                        product_id=msg_params,
                        edit_product = False,
                        delete_product = True).pack()
                        )
                ],
                [
                    InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='LEAVE_PRODUCT_EDIT')
                ]
            ])

            await message.answer(
                parse_mode='HTML',
                text=LEXICON_RU['EDIT_PRODUCT_CARD'].format(
                    name=current_product[1],
                    description=current_product[2],
                    price=current_product[3]
                ),
                reply_markup=current_kb
            )
        else:
            await message.answer(
                parse_mode='HTML',
                text=LEXICON_RU['ERROR_GETTING_PRODUCT_BY_SELLER']
            )
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ERROR_GETTING_PRODUCT_BY_SELLER']
        )

@seller_router.callback_query(ProductCardInteraction.filter(F.edit_product == True), StateFilter(default_state))
async def process_edit_product_start(callback: CallbackQuery, cached_db: CachedDatabase, callback_data: CallbackData, state: FSMContext):
    await state.set_state(CurrentProduct.product_id)
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(CurrentProduct.name)

    await callback.answer('')
    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['NEW_PRODUCT_NAME']
    )

@seller_router.message(Command(commands=['cancel_edit_product']), ~StateFilter(default_state))
async def process_edit_product_seller_cancel(message: Message, db: Database, state: FSMContext):
    await state.clear()

    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['CANCEL_EDIT_PRODUCT'],
        show_alert=True
    )

@seller_router.message(and_f(StateFilter(CurrentProduct.name), CheckAllowedSymbols()))
async def process_change_name_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await state.set_state(CurrentProduct.description)
    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['NEW_PRODUCT_DESCRIPTION']
    )

@seller_router.message(and_f(StateFilter(CurrentProduct.description), CheckAllowedSymbols()))
async def process_change_description_product(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    await state.set_state(CurrentProduct.price)
    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['NEW_PRODUCT_PRICE']
    )

@seller_router.message(and_f(StateFilter(CurrentProduct.price), CheckAllowedSymbolsDigit()))
async def process_change_description_product(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    result = await state.get_data()
    await state.clear()
    db.change_product_info(
        product_id=result['product_id'],
        name=result['name'],
        description=result['description'],
        price=result['price']
    )
    
    await message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SUCCESSFULL_CHANGE_PRODUCT']
    )

    time.sleep(0.7)
    await message.delete()

# Удаление карточки товара
@seller_router.callback_query(ProductCardInteraction.filter(F.delete_product == True), StateFilter(default_state))
async def process_delete_product_seller(callback: CallbackQuery, db: Database, callback_data: CallbackData, state: FSMContext):
    cur_product_to_delete = db.get_current_product_info(product_id=callback_data.product_id)

    await state.set_state(DeleteProductCardConfirm.product_price)
    await state.update_data(product_price=cur_product_to_delete[3])
    await state.set_state(DeleteProductCardConfirm.product_id)
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(DeleteProductCardConfirm.confirm)

    confrim_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['DECLINE_DELETE_PRODUCT_CARD'], callback_data=DeletingProductCard(
                product_id=callback_data.product_id, confirm_deleting=False).pack()
                ),
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CONFIRM_DELETE_PRODUCT_CARD'], callback_data=DeletingProductCard(
                product_id=callback_data.product_id, confirm_deleting=True).pack()),
        ]
    ])

    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['DELETING_PRODUCT_CARD_CONFIRMATION_MESSAGE'],
        reply_markup=confrim_keyboard
    )
# обработать согласие на удаление + отмену удаления
@seller_router.callback_query(and_f(StateFilter(DeleteProductCardConfirm.confirm), DeletingProductCard.filter(F.confirm_deleting == True)))
async def process_delete_product_seller_confirmation(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext, db: Database):
    current_product_price = db.get_current_product_info(product_id=callback_data.product_id)[3]
    await state.update_data(confirm=True)
    await state.set_state(DeleteProductCardConfirm.confirm_product_price)

    await callback.message.edit_text(
        parse_mode='HTML',
        text=LEXICON_RU['CONFIRM_DELETING_PRODUCT_CARD_WITH_PRICE_MESSAGE'].format(
            price=current_product_price
        )
    )

@seller_router.message(and_f(StateFilter(DeleteProductCardConfirm.confirm_product_price), CheckAllowedSymbolsDigit()))
async def process_delete_product_seller_confirmation_price(message: Message, state: FSMContext, db: Database):
    result = await state.get_data()

    if int(message.text) == result['product_price']:
        await state.clear()

        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['SUCCESSFULL_DELETE_PRODUCT_CARD']
        )

        db.delete_product(result['product_id'])
    else:
        await state.clear()
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['WRONG_CONFIRMATION_PRICE']
        )

@seller_router.callback_query(and_f(and_f(StateFilter(DeleteProductCardConfirm.confirm), DeletingProductCard.filter(F.confirm_deleting == False))))
async def process_delete_product_seller_confirmation(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    
    await callback.message.delete()

    await callback.answer(
        text=LEXICON_RU['DECLINED_DELETE_PRODUCT_CARD_ALERT'],
        show_alert=True
    )

# выход из редактирования продукта
@seller_router.callback_query(F.data == 'LEAVE_PRODUCT_EDIT')
async def process_leave_product_edit(callback: CallbackQuery):
    await callback.message.delete()

# просмотр статистики магазина
@seller_router.callback_query(MyShopPanel.filter(F.check_shop_stats==True))
async def process_check_shop_stats(callback: CallbackQuery, db: Database, callback_data: CallbackData):
    await callback.answer('')

    current_shop = db.get_current_shop_info(current_shop=callback_data.shop_id)
    result = prepare_shop_statistics(db.get_shop_statictics(shop_id=callback_data.shop_id))

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction')
        ]
    ])

    await callback.message.answer(
        parse_mode='HTML',
        text=LEXICON_RU['SHOP_STATISTICS_MESSAGE'].format(
            name=current_shop[1],
            total_count=result['total_count'],
            total_sum=result['total_sum']
        ),
        reply_markup=cancel_kb
    )

@seller_router.callback_query(MyShopPanel.filter(F.check_shop_orders==True))
async def process_check_shop_orders(callback: CallbackQuery, db: Database, callback_data: CallbackData):
    await callback.answer('')

    orders = db.get_shop_statictics(shop_id=callback_data.shop_id)
    current_kb = prepare_orders_for_seller(orders=orders)

    return_message = prepare_text_orders(orders=orders)

    await callback.message.answer(
        parse_mode='HTML',
        text=return_message,
        reply_markup=current_kb
    )

@seller_router.message(Command(commands=['order']))
async def process_get_info_about_active_order_text(message: Message, db: Database):
    msg_params = message.text.split(' ')[1]
    current_order = db.get_order(order_id=msg_params)

    
    if db.get_current_shop_info(current_shop=current_order[0])[0] == str(message.from_user.id):
        current_products = db.get_products_names_with_id(current_order[2])

        if current_order[-2] == 'Active':
            current_keyboard = active_order_keyboard(order_id=msg_params)
        elif current_order[-2] == 'In Progress':
            current_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LEXICON_RU_BUTTONS['COMPLETE_ORDER'], callback_data=CompleteOrder(user_id=message.from_user.id, order_id=msg_params, is_seller=True).pack())
                ],
                [
                    InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction')
                ]
        ])
        elif current_order[-2] == 'Completed':
            current_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction')
        ]
        ])

        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['INFO_ABOUT_ACTIVE_ORDER_MESSAGE'].format(
                order_id=current_order[-1],
                buyer_id=current_order[1],
                products=current_products[2],
                room=current_order[3],
                total_sum=current_order[-3]
            ),
            reply_markup=current_keyboard
        )
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ERROR_ORDER_NUM']
        )

        time.sleep(3)
        message.delete()

@seller_router.callback_query(CompleteOrder.filter(F.is_seller == True))
async def process_complete_order_by_user(callback: CallbackQuery, callback_data: CallbackData, db: Database):
    current_order = db.get_order(order_id=callback_data.order_id)

    if db.get_current_shop_info(current_shop=current_order[0])[0] == str(callback.from_user.id):
        await callback.message.delete()

        db.complete_order(order_id=callback_data.order_id)

        await callback.message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ORDER_COMPLETED_BY_SELLER'].format(order_id=callback_data.order_id)
        )
    else:
        await callback.message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ERROR_BY_CLOSING_ORDER_BY_SELLER']
        )

@seller_router.callback_query(HandleOrderBySeller.filter())
async def processing_order_by_seller(callback: CallbackQuery, callback_data: CallbackData, cached_db: CachedDatabase, db: Database):
    if callback_data.accept_order:
        db.change_order_status_to_in_progress(order_id=callback_data.order_id)
        cached_db.set_values(f'handle_order:id{callback.from_user.id}', tuple([True, callback_data.order_id]))

        await callback.message.delete()

        await callback.answer(
            text=LEXICON_RU['ACCEPTED_ORDER_BY_SELLER_MESSAGE'],
            show_alert=True
        )

    else:
        db.delete_order(order_id=callback_data.order_id)
        cached_db.set_values(f'handle_order:id{callback.from_user.id}', tuple([False, callback_data.order_id]))

        await callback.message.delete()

        await callback.answer(
            text=LEXICON_RU['DECLINED_ORDER_BY_SELLER_MESSAGE'],
            show_alert=True
        )