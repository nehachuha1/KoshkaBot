from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters.filters import MyShopPanel
from lexicon.lexicon import LEXICON_RU, LEXICON_RU_BUTTONS
from database.database import Database

def build_myshop_main_kb(shop_id: int = None, admin_id: int = None, db: Database = None):
    current_shop = db.get_current_shop_info(current_shop=shop_id)
    myshop_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_SHOP_INFO'], callback_data=MyShopPanel(
                shop_id=shop_id, admin_id=admin_id, edit_shop_info=True).pack()),
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS[f'EDIT_SHOP_STATUS_{current_shop[3].upper()}'], callback_data=MyShopPanel(
                shop_id=shop_id, admin_id=admin_id, edit_shop_status=True).pack())
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CHECK_SHOP_STATS'], callback_data=MyShopPanel(
                shop_id=shop_id, admin_id=admin_id, check_shop_stats=True).pack()),
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['EDIT_PRODUCTS_LIST'], callback_data=MyShopPanel(
                shop_id=shop_id, admin_id=admin_id, edit_products_list=True).pack()),
        ],
        [
            InlineKeyboardButton(text=LEXICON_RU_BUTTONS['CHECK_SHOP_ORDERS'], callback_data=MyShopPanel(
                shop_id=shop_id, admin_id=admin_id, check_shop_orders=True).pack())
        ]
    ])
    return myshop_kb