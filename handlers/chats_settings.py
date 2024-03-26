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

async def get_chat_id(link: str) -> int:
    try:
        chat = await aiogram_bot.get_chat(link)
        return chat.id
    except Exception as e:
        logger.error(e)
        return 'No'

async def groups_settings(message):
    uid = message.from_user.id
    chats_list = await db.get_monitor_list(uid)

    if chats_list != 'Нет':
        string = ''
        print(chats_list)
        for chat in chats_list:
            string += f'\n{chat}'
    else:
        string = chats_list
    await message.answer('<b>Список чатов Telegram: </b>'
                         f'\n{string}', reply_markup=main_kb.chats_action(), parse_mode='HTML')


@router.callback_query(F.data == 'tg_groups')
async def p_groups(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    chats_list = await db.get_monitor_list(uid)

    if chats_list != 'Нет':
        string = ''
        for chat in chats_list:
            string += f'\n{chat}'
    else:
        string = chats_list
    await callback.message.answer('<b>Список чатов Telegram: </b>'
                                  f'\n{string}', reply_markup=main_kb.chats_action(), parse_mode='HTML')


@router.callback_query(F.data == 'add_chat')
async def p_add_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ссылку на чат:')
    await state.set_state(states.AddChat.input_chat)


@router.message(states.AddChat.input_chat)
async def save_chat(message: Message, state: FSMContext):
    new_chat = message.text
    chat_id = await get_chat_id(new_chat)
    uid = message.from_user.id
    try:
        await db.add_to_monitor_list(uid, new_chat,chat_id)
        await message.answer('Чат добавлен.')

    except Exception as e:
        logger.error(f'Ошибка при добавлении чата: {e}')
        await message.answer('Ошибка при добавлении чата.')

    finally:
        await state.clear()
        await groups_settings(message)


@router.callback_query(F.data == 'del_chat')
async def p_del_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ссылку для удаления: ')
    await state.set_state(states.DelChat.input_chat)


@router.message(states.DelChat.input_chat)
async def chat_deleted(message: Message, state: FSMContext):
    del_chat = message.text
    uid = message.from_user.id
    try:
        await db.remove_from_monitor_list(uid, del_chat)
        await message.answer(f'Чат [{del_chat}] удален из списка чатов.')
        await groups_settings(message)
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при удалении чата.')
    finally:
        await state.clear()

