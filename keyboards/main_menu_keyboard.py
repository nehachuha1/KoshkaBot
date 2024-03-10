from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import LEXICON_RU_BUTTONS

main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['STATS_BUTTON'],
                             callback_data='check_user_stats'),
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['BOT_INFO_BUTTON'],
                             callback_data='about_bot_info')
    ],
    [
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CHECK_SHOPS'],
                             callback_data='get_list_of_shops'),
    ],
    [
        InlineKeyboardButton(text=LEXICON_RU_BUTTONS['MY_ORDERS'],
                             callback_data='my_orders')
    ]
])