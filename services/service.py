from aiogram.fsm.state import StatesGroup, State
from lexicon.lexicon import LEXICON_RU

class RegistrationFillForm(StatesGroup):
    username = State()
    full_name = State()
    room = State()
    is_seller = State()

def prepare_user_info(user_info: tuple = None):
    return LEXICON_RU['USER_INFO'].format(tg_id=user_info[0],
                                          full_name=user_info[1],
                                          room=user_info[2],
                                          orders_count=0 if not user_info[3] else user_info[3])