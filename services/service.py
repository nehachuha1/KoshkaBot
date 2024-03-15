from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton

from lexicon.lexicon import LEXICON_RU
from filters.filters import ProductInfoFilter, SellerProductInfoFilter

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