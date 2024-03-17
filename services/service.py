from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import ProductInfoFilter, SellerProductInfoFilter, HandleOrderBySeller
from database.database import Database

class RegistrationFillForm(StatesGroup):
    username = State()
    full_name = State()
    room = State()
    is_seller = State()

class OrderFillForm(StatesGroup):
    username = State()
    room = State()
    product_name = State()
    price = State()
    shop_id = State()
    product_id = State()

class CurrentProduct(StatesGroup):
    product_id = State()
    name = State()
    description = State()
    price = State()

class DeleteProductCardConfirm(StatesGroup):
    product_price = State()
    product_id = State()
    confirm = State()
    confirm_product_price = State()

class ChangeShopName(StatesGroup):
    shop_name = State()

class ChangeShopDescription(StatesGroup):
    shop_description = State()

class ChangeUserRoom(StatesGroup):
    user_room = State()

class ChangeShopPhoto(StatesGroup):
    shop_photo = State()

def prepare_user_info(user_info: tuple = None):
    return LEXICON_RU['USER_INFO'].format(tg_id=user_info[0],
                                          full_name=user_info[1],
                                          room=user_info[2],
                                          is_seller=user_info[3],
                                          orders_count=0 if not user_info[4] else user_info[4])

def prepare_list_products_shop(products: tuple = None) -> list:
    buttons = list()

    for product in products:
        button = InlineKeyboardButton(
            text=product[1],
            callback_data=ProductInfoFilter(
                shop_id=product[0],
                name=product[1],
                product_id=product[-1]
            ).pack()
        )

        buttons.append(button)
    return buttons

def prepare_list_products_shop_seller(products: tuple = None) -> list:
    buttons = list()

    for product in products:
        button = InlineKeyboardButton(
            text=product[1],
            callback_data=SellerProductInfoFilter(
                shop_id=product[0],
                name=product[1],
                product_id=product[-1]
            ).pack()
        )

        buttons.append(button)
    return buttons

def prepare_shop_statistics(orders: list = None):
    result = dict()

    result['total_count'] = len(orders)
    result['total_sum'] = 0

    for order in orders:
        result['total_sum'] += order[5]
    
    return result

async def send_notification_to_seller(shop_id:int = None, bot: Bot = None, db: Database = None):
    admin_chat_id = db.get_current_shop_info(current_shop=shop_id)[0]
    await bot.send_message(
        chat_id=admin_chat_id,
        parse_mode='HTML',
        text=LEXICON_RU['NEW_ORDER_NOTIFICATION']
    )

def active_order_keyboard(order_id: int = None):
    active_order_kb = InlineKeyboardBuilder()

    accept_btn = InlineKeyboardButton(
        text=LEXICON_RU_BUTTONS['ACCEPT_ORDER_FROM_USER'],
        callback_data=HandleOrderBySeller(order_id=order_id, accept_order=True).pack()
    )
    decline_btn = InlineKeyboardButton(
        text=LEXICON_RU_BUTTONS['DECLINE_ORDER_FROM_USER'],
        callback_data=HandleOrderBySeller(order_id=order_id, accept_order=False).pack()
    )

    active_order_kb.add(accept_btn, decline_btn)

    return active_order_kb.as_markup()

async def send_notification_to_buyer(order_id:int = None, bot: Bot = None, db: Database = None, accepted: bool = None):
    current_order = db.get_order(order_id=order_id)
    if accepted:
        await bot.send_message(
            chat_id = current_order[1],
            parse_mode='HTML',
            text=LEXICON_RU['SELLER_ACCEPTED_YOUR_ORDER_MESSAGE']
        )
    else:
        await bot.send_message(
            chat_id = current_order[1],
            parse_mode='HTML',
            text=LEXICON_RU['SELLER_DECLINED_YOUR_ORDER_MESSAGE']
        )

def prepare_text_orders(orders: list) -> str:
    result = str()

    result += LEXICON_RU['SHOP_ORDERS_MESSAGE'] + '\n\n'

    for order in orders:
        result += f'Order #{order[1]}: {order[-1]}\n'
    return result

def prepare_user_orders_text(orders: list) -> str:
    result = str()

    result += LEXICON_RU['SHOP_ORDERS_USER_MESSAGE'] + '\n\n'

    for order in orders:
        result += f'Order #{order[-1]}: {order[-2]}\n'
    return result