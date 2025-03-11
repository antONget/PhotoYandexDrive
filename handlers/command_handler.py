import logging

from aiogram import F, Router, Bot
from aiogram.types import Message
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
            # download = await get_download_link(order.path_folder)
            view = await get_photo_view_link(order.path_folder)
            await message.answer(text=f'<b>Дата покупки:</b> {order.date_payment}\n'
                                      f'<b>Событие:</b> {order.event} - <b>экипаж:</b> {order.team}\n'
                                      f'📄 Ссылка для просмотра: {view}')
    else:
        await message.answer("Вы еще не совершали заказов")


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