from aiogram.filters.callback_data import CallbackData

class ShopInteraction(CallbackData, prefix='shop'):
    shop_id: int
    to_return: bool

class ProductInfoFilter(CallbackData, prefix='product'):
    shop_id: int
    name: str
    product_id: int

class OrderProductFilter(CallbackData, prefix='order_product'):
    shop_id: int
    product_id: int

class ProcessingUserOrder(CallbackData, prefix='processing_order'):
    accepted: bool