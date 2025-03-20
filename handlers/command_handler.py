import logging

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import database.requests as rq
from database.models import Order
from config_data.config import Config, load_config
from services.yandex_drive import get_download_link, get_photo_view_link

router = Router()
config: Config = load_config()


@router.message(Command('order'))
async def command_orders(message: Message, bot: Bot) -> None:
    """
    Вывод заказов
    :param message:
    :param bot:
    :return:
    """
    logging.info('command_orders')
    tg_id: int = message.from_user.id
    orders: list[Order] = await rq.get_orders_tg_id(tg_id=tg_id)
    if orders:
        for order in orders:
            original_path = order.path_folder.replace('preview', 'original')
            print(original_path)
            view = await get_photo_view_link(file_path=original_path)
            await message.answer(text=f'<b>{order.event}, экипаж {order.team}</b>\n'
                                      f'покупка от: {order.date_payment}\n'
                                      f'{view}')
    else:
        await message.answer("Вы еще не совершали заказов")


@router.callback_query(F.data == 'show_orders')
async def command_orders_callback(callback: CallbackQuery, bot: Bot) -> None:
    """
    Вывод заказов
    :param callback:
    :param bot:
    :return:
    """
    logging.info('command_orders')
    tg_id: int = callback.from_user.id
    orders: list[Order] = await rq.get_orders_tg_id(tg_id=tg_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    if orders:
        for order in orders:
            # download = await get_download_link(order.path_folder)
            original_path = order.path_folder.replace('preview', 'original')
            print(original_path)
            view = await get_photo_view_link(file_path=original_path)
            await callback.message.answer(text=f'<b>{order.event}, экипаж {order.team}</b>\n'
                                               f'покупка от: {order.date_payment}\n'
                                               f'{view}')
    else:
        await callback.answer(text="Вы еще не совершали заказов",
                              show_alert=True)
    await callback.answer()


@router.message(Command('help'))
async def command_help(message: Message, bot: Bot) -> None:
    """
    Помощь
    :param message:
    :param bot:
    :return:
    """
    logging.info('command_help')
    await message.answer(text='это текстовый месcедж про цену/цены')


@router.message(Command('support'))
async def command_support(message: Message, bot: Bot) -> None:
    """
    Поддержка
    :param message:
    :param bot:
    :return:
    """
    logging.info('command_support')
    await message.answer(text='Если у вас возникли вопросы по работе бота, сложности при оплате заказа или есть'
                              ' предложения по улучшению функционала напишите мне @SanAndreasFPV')


@router.message(Command('clear'))
async def command_clear(message: Message, bot: Bot) -> None:
    """
    Поддержка
    :param message:
    :param bot:
    :return:
    """
    logging.info('command_support')
    for i in range(100):
        try:
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=message.message_id - i)
        except:
            pass
