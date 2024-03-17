from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from lexicon.lexicon import LEXICON_RU_BUTTONS

def get_shop_products_kb(buttons: list = None) -> InlineKeyboardBuilder:
    shop_kb = InlineKeyboardBuilder()

    for button in buttons:
        shop_kb.add(button)
    
    pag_and_cancel_buttons = [
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['<-'], callback_data='PREVIOUS_PAGE_PRODUCTS'),
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['->'], callback_data='NEXT_PAGE_PRODUCTS'),
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['LEAVE_PRODUCTS_LIST_BUTTON'], callback_data='LEAVE_PRODUCTS_LIST_BUTTON')
    ]
    shop_kb.add(*pag_and_cancel_buttons)

    sizes = [1 for _ in range(len(buttons))]
    sizes.append(2)

    shop_kb.adjust(*sizes)

    return shop_kb

# def get_shop_products_kb_seller(buttons: list = None) -> InlineKeyboardBuilder:
#     shop_kb = InlineKeyboardBuilder()

#     for button in buttons:
#         shop_kb.add(button)
    
#     pag_and_cancel_buttons = [
#         InlineKeyboardButton(text=LEXICON_RU_BUTTONS['<-'], callback_data='PREVIOUS_PAGE_PRODUCTS'),
#         InlineKeyboardButton(text=LEXICON_RU_BUTTONS['->'], callback_data='NEXT_PAGE_PRODUCTS'),
#         InlineKeyboardButton(text=LEXICON_RU_BUTTONS['LEAVE_PRODUCTS_LIST_BUTTON'], callback_data='cancel_editing_shop_info')
#     ]
#     shop_kb.add(*pag_and_cancel_buttons)

#     sizes = [1 for _ in range(len(buttons))]
#     sizes.append(2)

#     shop_kb.adjust(*sizes)

#     return shop_kb