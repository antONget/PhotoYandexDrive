import logging

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database.requests as rq


def keyboard_start() -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :return:
    """
    logging.info('keyboard_start')
    button_1 = KeyboardButton(text='Персонал')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_preview_folder( id_frame: int) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Хочу приобрести эти фото', callback_data=f'semiautopay_{id_frame}')
    button_2 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    button_3 = InlineKeyboardButton(text='Спасибо, не в это раз', callback_data='cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard


def keyboard_not_public_link() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    button_2 = InlineKeyboardButton(text='Спасибо, не в это раз', callback_data='cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard
