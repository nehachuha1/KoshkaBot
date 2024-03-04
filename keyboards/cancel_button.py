from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon import LEXICON_RU_BUTTONS

cancel_button = InlineKeyboardButton(text=LEXICON_RU_BUTTONS["CANCEL"], callback_data='cancel')

cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])