import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from filters.is_admin import IsAdmin
from keyboards import main_kb
from utils import json_action
from states import states
from database import db
router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'user_lk')
async def p_lk(callback: CallbackQuery):
    uid = callback.from_user.id
    user_info = await db.get_user_info(uid)
    await callback.message.answer(user_info, parse_mode='HTML')