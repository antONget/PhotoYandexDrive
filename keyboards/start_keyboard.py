from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database.requests as rq

def keyboard_start(role: str) -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :param role:
    :return:
    """

    if role == rq.UserRole.admin:
        button_1 = KeyboardButton(text='Персонал')
        button_2 = KeyboardButton(text='Создать заказ')
        button_3 = KeyboardButton(text='Заказы')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3]],
                                       resize_keyboard=True)
    else:
        button_1 = KeyboardButton(text='Создать заказ')
        button_2 = KeyboardButton(text='Заказы')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                       resize_keyboard=True)

    return keyboard


def keyboard_preview_folder( id_frame: int) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Хочу приобрести эти фото', callback_data=f'semiautopay_{id_frame}')
    button_2 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    button_3 = InlineKeyboardButton(text='Спасибо, не в это раз', callback_data='cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard

