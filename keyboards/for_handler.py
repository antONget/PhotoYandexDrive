from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import UserRole
from database.models import User, Order
from filter.admin_filter import check_super_admin
import logging

def keyboards_orders(list_users: list[Order], back, forward, count) -> InlineKeyboardMarkup:
    """
    Список пользователей для удаления из персонала
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_del_personal')
    print(back, forward)
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward >= max_forward:
        forward = max_forward
        back = forward - 2
    print(back, forward, max_forward)
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    a=1
    for order in list_users[back*count:(forward-1)*count]:
        text = a
        a+=1
        button = f'order_{order.frame_id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'order_back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'order_forward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()