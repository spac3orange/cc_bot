from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger
from filters.is_admin import IsAdmin
from keyboards import main_kb
from utils import monitor_obj
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    logger.info(f'user {message.from_user.username} connected')
    await state.clear()
    status = 'Выключен' if not await monitor_obj.get_status() else 'Включен'
    interval = await monitor_obj.get_interval()
    await message.answer('<b>Добро пожаловать!</b>'
                         f'\n\n<b>Статус:</b> {status}'
                         f'\n<b>Интервал мониторинга:</b> {interval}',
                         reply_markup=main_kb.start_btns(), parse_mode='HTML')


@router.callback_query(F.data == 'bot_start')
async def m_start(callback: CallbackQuery):
    await callback.answer()
    await monitor_obj.start_monitoring()
    await callback.message.answer('Мониторинг чатов запущен.')


@router.callback_query(F.data == 'bot_stop')
async def m_stop(callback: CallbackQuery):
    await callback.answer()
    await monitor_obj.stop_monitoring()
    await callback.message.answer('Мониторинг чатов выключен.')

@router.message(Command('status'))
async def p_status(message: Message):
    status = await monitor_obj.get_status()
    status = 'Работает' if status else 'Выключен'
    await message.answer(f'Мониторинг {status}')