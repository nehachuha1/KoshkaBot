from keyboards.pagination_keyboard import build_pagination_keyboard
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.filters import ShopInteraction

from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS

def shop_interaction_kb(current_page:int = 1, type: int = 1, shop_id: int = None):
    if type == 1:
        current_kb = build_pagination_keyboard(current_page=current_page, to_return=2)
        current_kb.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS["VISIT_SHOP"], callback_data=ShopInteraction(shop_id=shop_id, to_return=False).pack())) #исправить инлайн кнопку на фабрику колбэков
        current_kb.add(InlineKeyboardButton(text=LEXICON_RU_BUTTONS["CANCEL"], callback_data='cancel_from_shops'))
        current_kb.adjust(3, 1, 1)

        return current_kb