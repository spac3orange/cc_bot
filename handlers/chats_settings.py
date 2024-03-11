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
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def groups_settings(message):
    chats_list = await json_action.open_json('data/chats.json')
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
    chats_list = await json_action.open_json('data/chats.json')
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
    chats_lst = await json_action.open_json('data/chats.json')
    if chats_lst == 'Нет':
        chats_lst = [new_chat]
    else:
        chats_lst.append(new_chat)
    filename = 'chats.json'
    await json_action.write_json(chats_lst, filename)
    await message.answer('Чат добавлен.')
    chats_lst = await json_action.open_json('data/chats.json')
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
    chats_list = await json_action.open_json('data/chats.json')
    if chats_list == 'Нет':
        await message.answer('Список чатов пуст.')
        await state.clear()
    else:
        if del_chat in chats_list:
            chats_list.remove(del_chat)
            await json_action.write_json(chats_list, 'chats.json')
            await message.answer(f'Чат [{del_chat}] удален из списка чатов.')
            await groups_settings(message)
        else:
            await message.answer(f'Чат [{del_chat}] не найден в списке чатов.')
        await state.clear()
