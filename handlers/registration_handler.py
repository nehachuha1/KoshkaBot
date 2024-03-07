from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.types import Message
from aiogram import Router, F

from services.service import RegistrationFillForm
from database.database import CachedDatabase
from lexicon.lexicon import LEXICON_RU

registration_router = Router()

@registration_router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, is_registered: bool):
    if is_registered:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['/start_registered']
        )
    elif not is_registered:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['/start'])
# cancel в самом начале регистрации
@registration_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_without_state(message: Message, state: FSMContext):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['error_cancel_on_registration_default'])
    await state.clear()
# cancel на одном из шагов
@registration_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_without_state(message: Message, state: FSMContext):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['error_cancel_on_registration'])
    await state.clear()

@registration_router.message(Command(commands='register'), StateFilter(default_state))
async def process_register_command(message: Message, state: FSMContext, is_registered: bool):
    if not is_registered:
        await message.answer(parse_mode='HTML',
                            text=LEXICON_RU['registrate_start'])
        await state.set_state(RegistrationFillForm.username)
        await state.update_data(username=message.from_user.id)
        await state.set_state(RegistrationFillForm.full_name)
        await state.update_data(full_name=message.from_user.full_name)
        await state.set_state(RegistrationFillForm.room)
    else:
        await message.answer(
            parse_mode='HTML',
            text=LEXICON_RU['ALREADY_REGISTERED']
        )

@registration_router.message(StateFilter(RegistrationFillForm.room), F.text.isdigit())
async def process_room_accept_command(message: Message, state: FSMContext, cached_db: CachedDatabase):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['registrate_room_accept'])
    await state.update_data(room=message.text)
    await state.set_state(RegistrationFillForm.is_seller)
    await state.update_data(is_seller = False)
    
    result = await state.get_data()
    cached_db.set_values(str(message.from_user.id), result)
    await state.clear()
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['to_use_menu'])

@registration_router.message(StateFilter(RegistrationFillForm.room), ~F.text.isdigit())
async def process_room_decline_command(message: Message, state: FSMContext):
    await message.answer(parse_mode='HTML',
                         text=LEXICON_RU['error_room_input'])
    
