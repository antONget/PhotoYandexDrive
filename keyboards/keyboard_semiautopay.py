from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


def keyboard_send_check(id_frame: int) -> InlineKeyboardMarkup:
    logging.info("keyboard_send_check")
    button_1 = InlineKeyboardButton(text='отправить чек об оплате',  callback_data=f'send_check_{id_frame}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_check_payment(order_id: int) -> InlineKeyboardMarkup:
    logging.info("keyboard_check_payment")
    button_1 = InlineKeyboardButton(text='Спам',  callback_data=f'payment_cancel_{order_id}')
    button_2 = InlineKeyboardButton(text='Подтвердить', callback_data=f'payment_confirm_{order_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
    return keyboard
