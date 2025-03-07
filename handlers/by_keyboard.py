from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

import keyboards.keyboards_edit_list_personal as kb
from keyboards.for_handler import keyboards_orders
import database.requests as rq
from database.models import User
from filter.admin_filter import IsSuperAdmin
from utils.error_handling import error_handler
from config_data.config import Config, load_config

from uuid import uuid4
import asyncio
import logging

router = Router()
config: Config = load_config()

@router.message(F.text == 'Заказы')
async def process_change_list_personal(message: Message, bot: Bot) -> None:
    tg_id: int = message.from_user.id
    orders = await rq.get_order_by_tg_id(tg_id)

    if orders =="0":
        await message.answer("Вы еще не заказывали фотогрфии")
    else:
        await message.answer("вот ваши заказы", reply_markup=keyboards_orders(orders,
                                                                                   back=0,
                                                                                   forward=2,
                                                                                    count=6))

