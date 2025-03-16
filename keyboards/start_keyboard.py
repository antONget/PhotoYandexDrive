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


def keyboard_preview_folder(id_frame: int, num_team: str) -> InlineKeyboardMarkup:
    """
    [['Хочу приобрести эти фото'], ['Посмотреть другой экипаж'], ['Спасибо, не в это раз']]
    :param id_frame:
    :param num_team:
    :return:
    """
    button_1 = InlineKeyboardButton(text='Хочу приобрести эти фото',
                                    callback_data=f'semiautopay!@!{id_frame}!@!{num_team}')
    button_2 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    button_3 = InlineKeyboardButton(text='Спасибо, не в этот раз', callback_data='cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard


def keyboard_preview_cancel(id_frame: int, path_team: str) -> InlineKeyboardMarkup:
    """
    [['Хочу приобрести эти фото'], ['Посмотреть другой экипаж'], ['Спасибо, не в это раз']]
    :param id_frame:
    :param path_team:
    :return:
    """
    button_1 = InlineKeyboardButton(text='Хочу приобрести эти фото',
                                    callback_data=f'semiautopay!@!{id_frame}!@!{path_team}')
    button_2 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_not_public_link() -> InlineKeyboardMarkup:
    """
    [['Посмотреть другой экипаж']]
    :return:
    """
    button_1 = InlineKeyboardButton(text='Посмотреть другой экипаж', callback_data='other_team')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_wish(id_frame: int, num_team: str) -> InlineKeyboardMarkup:
    """
    [['Хочу приобрести эти фото']]
    :param id_frame:
    :param num_team:
    :return:
    """
    button_1 = InlineKeyboardButton(text='Хочу приобрести эти фото',
                                    callback_data=f'semiautopay!@!{id_frame}!@!{num_team}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard
