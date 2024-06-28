from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    kb = [
        [
            types.KeyboardButton(text="Добавить пробежку"),
            types.KeyboardButton(text="Мои пробежки")
        ],
        [
            types.KeyboardButton(text="Добавить кроссовки"),
            types.KeyboardButton(text="Мои кроссовки")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    return keyboard


def check_data():
    kb_list = [
        [InlineKeyboardButton(text="✅Все верно", callback_data='correct')],
        [InlineKeyboardButton(text="❌Заполнить сначала", callback_data='incorrect')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def miss_field():
    kb_list = [
        [InlineKeyboardButton(text="Пропустить", callback_data='miss_field')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard
