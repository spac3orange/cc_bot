from aiogram.fsm.state import StatesGroup, State


class AddKw(StatesGroup):
    input_kw = State()


class DelKw(StatesGroup):
    input_kw = State()


class AddChat(StatesGroup):
    input_chat = State()


class DelChat(StatesGroup):
    input_chat = State()


class IntSet(StatesGroup):
    input_interval = State()