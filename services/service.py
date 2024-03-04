from aiogram.fsm.state import StatesGroup, State

class RegistrationFillForm(StatesGroup):
    username = State()
    full_name = State()
    room = State()
    is_seller = State()