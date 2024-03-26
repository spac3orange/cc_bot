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


async def kw_settings(message):
    uid = message.from_user.id
    keywords_list = await db.get_all_keywords(uid)
    await message.answer('<b>Список текущих установленных ключевых слов: </b>'
                         f'\n{keywords_list}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'keywords')
async def p_keywords(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    keywords_list = await db.get_all_keywords(uid)
    await callback.message.answer('<b>Список текущих установленных ключевых слов: </b>'
                                  f'\n{keywords_list}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'add_kw')
async def p_add_kw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите новое ключевое слово:')
    await state.set_state(states.AddKw.input_kw)


@router.message(states.AddKw.input_kw)
async def save_kw(message: Message, state: FSMContext):
    new_kw = message.text
    uid = message.from_user.id
    try:
        await db.add_keywords(uid, new_kw)
        await message.answer('Ключевое слово успешно добавлено.')
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при добавлении ключевого слова.')
    finally:
        await state.clear()
        keywords_list = await db.get_all_keywords(uid)
        await message.answer('<b>Список ключевых слов: </b>'
                             f'\n{keywords_list}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'del_kw')
async def p_del_kw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ключевое слово для удаления: ')
    await state.set_state(states.DelKw.input_kw)


@router.message(states.DelKw.input_kw)
async def kw_deleted(message: Message, state: FSMContext):
    uid = message.from_user.id
    del_kw = message.text
    try:
        await db.remove_keywords(uid, del_kw)
        await message.answer(f'Ключевое слово [{del_kw}] успешно удалено.')
        await kw_settings(message)
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при удалении ключевого слова.')
    finally:
        await state.clear()
