from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from filters.filters import ActiveOrder

def prepare_orders_for_seller(orders: list = None):
    orders_keyboard = InlineKeyboardBuilder()
    
    orders_keyboard.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CANCEL'], callback_data='cancel_button_shop_interaction'))
    orders_keyboard.adjust(1)

    return orders_keyboard.as_markup()
