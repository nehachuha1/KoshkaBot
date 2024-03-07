from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton

from lexicon.lexicon import LEXICON_RU
from filters.filters import ProductInfoFilter

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

def prepare_user_info(user_info: tuple = None):
    return LEXICON_RU['USER_INFO'].format(tg_id=user_info[0],
                                          full_name=user_info[1],
                                          room=user_info[2],
                                          orders_count=0 if not user_info[3] else user_info[3])

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