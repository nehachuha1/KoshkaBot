from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_pagination_keyboard(current_page: int = 1, to_return: int = 1):
    pagination_kb = InlineKeyboardBuilder()

    cur_page = InlineKeyboardButton(text=f'{current_page}', callback_data='CURRENT_PAGE')

    left_button = InlineKeyboardButton(text='<-', callback_data='PREVIOUS_PAGE')
    right_button = InlineKeyboardButton(text='->', callback_data='NEXT_PAGE')

    pagination_kb.add(left_button, cur_page, right_button)
    pagination_kb.adjust(3)
    if to_return == 1:
        return pagination_kb.as_markup()
    else:
        # return list(left_button, cur_page, right_button)
        return pagination_kb