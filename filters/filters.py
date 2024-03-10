from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.filters import BaseFilter

from config.config import ALLOWED_SYMBOLS

class ShopInteraction(CallbackData, prefix='shop'):
    shop_id: int
    to_return: bool

class ProductInfoFilter(CallbackData, prefix='product'):
    shop_id: int
    name: str
    product_id: int

class SellerProductInfoFilter(CallbackData, prefix='seller_change_product'):
    shop_id: int
    name: str
    product_id: int

class OrderProductFilter(CallbackData, prefix='order_product'):
    shop_id: int
    product_id: int

class ProcessingUserOrder(CallbackData, prefix='processing_order'):
    accepted: bool

class MyShopPanel(CallbackData, prefix='myshop_panel'):
    shop_id: int
    admin_id: int
    edit_shop_info: bool = False
    edit_shop_status: bool = False
    check_shop_stats: bool = False
    edit_products_list: bool = False
    check_shop_orders: bool = False

class CheckAllowedSymbols(BaseFilter):
    def __init__(self) -> None:
        self.allowed_symbols = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя '
    async def __call__(self, message: Message) -> bool:
        flag = True
        for symbol in message.text:
            if symbol.lower() not in self.allowed_symbols:
                flag = False
        return flag