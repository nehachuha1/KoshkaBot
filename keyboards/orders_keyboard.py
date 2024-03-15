from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import ActiveOrder

def prepare_orders_for_seller(orders: list = None):
    orders_keyboard = InlineKeyboardBuilder()
    active_orders = [order for order in orders if order[-1] == 'Active']

    for order in active_orders:
        orders_keyboard.add(
            InlineKeyboardButton(
                text=LEXICON_RU_BUTTONS['ACTIVE_ORDER_SELLER_MENU'].format(order_id=order[1]),
                callback_data=ActiveOrder(
                    order_id=order[1],
                    buyer_id=order[2],
                    products_ids=' '.join(order[3]),
                    room=order[4]
                ).pack()
            )
        )
    orders_keyboard.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction'))
    orders_keyboard.adjust(1)

    return orders_keyboard.as_markup()
