import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from filters.is_admin import IsAdmin
from keyboards import main_kb
from utils import json_action, monitor_obj
from states import states
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'timing_settings')
async def p_interval_settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите новый интервал в минутах: ')
    await state.set_state(states.IntSet.input_interval)


@router.message(states.IntSet.input_interval)
async def p_set_int(message: Message, state: FSMContext):
    new_int = int(message.text) if message.text.isdigit() else 5
    await monitor_obj.set_interval(new_int)
    await message.answer(f'Интервал мониторинга успешно изменен на {new_int} минут.'
                         f'\nМониторинг был перезапущен.')

