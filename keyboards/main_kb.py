from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config_aiogram


def start_btns(uid):
    admins = config_aiogram.admin_id
    if uid in admins:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text='Запустить', callback_data='bot_start')
        kb_builder.button(text='Остановить', callback_data='bot_stop')
        kb_builder.button(text='Ключевые слова', callback_data='keywords')
        kb_builder.button(text='Чаты', callback_data='tg_groups')
        kb_builder.button(text='Интервал', callback_data='timing_settings')
    else:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text='Запустить', callback_data='bot_start')
        kb_builder.button(text='Остановить', callback_data='bot_stop')
        kb_builder.button(text='Ключевые слова', callback_data='keywords')
        kb_builder.button(text='Чаты', callback_data='tg_groups')
        kb_builder.button(text='Личный Кабинет', callback_data='user_lk')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def keywords_action():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='add_kw')
    kb_builder.button(text='Удалить', callback_data='del_kw')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def chats_action():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='add_chat')
    kb_builder.button(text='Удалить', callback_data='del_chat')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)