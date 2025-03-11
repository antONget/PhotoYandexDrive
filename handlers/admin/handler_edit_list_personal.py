from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup

import keyboards.admin.keyboards_edit_list_personal as kb
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


class Personal(StatesGroup):
    id_tg_personal = State()


# Персонал
@router.message(F.text == 'Персонал', IsSuperAdmin())
@error_handler
async def select_action_partner(message: Message, state: FSMContext,  bot: Bot) -> None:
    """
    Выбор роли для редактирования списка
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'select_action_partner: {message.chat.id}')
    role = '<b>ПАРТНЕРА</b>'
    await state.update_data(edit_role='partner')
    await message.answer(text=f"Назначить или разжаловать пользователя как {role}?",
                         reply_markup=kb.keyboard_select_action())


@router.callback_query(F.data == 'personal_add')
@error_handler
async def process_personal_add(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Действие добавления пользователя в список выбранной роли
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_personal_add: {callback.message.chat.id}')
    rand_token = str(uuid4())
    data = await state.get_data()
    edit_role = data['edit_role']
    role = '<b>ПАРТНЕРОВ</b>'
    token_data = {"token": rand_token,
                  "role": edit_role}
    await rq.add_token(data=token_data)
    await callback.message.edit_text(text=f'Для добавления пользователя в список {role}, '
                                          f'отправьте ему пригласительную ссылку:\n'
                                          f'<code>https://t.me/{config.tg_bot.link_bot}?start={rand_token}'
                                          f'</code>')
    await callback.answer()


@router.callback_query(F.data == 'personal_delete')
@error_handler
async def process_del_admin(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор пользователя для разжалования его из персонала
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_del_admin: {callback.message.chat.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    role = '<b>ПАРТНЕРОВ</b>'
    role_ = 'ПАРТНЕРОВ'
    list_users: list[User] = await rq.get_users_role(role=edit_role)
    if not list_users:
        await callback.answer(text=f'Нет пользователей для удаления из списка {role_}', show_alert=True)
        return
    keyboard = kb.keyboards_del_personal(list_users=list_users,
                                         back=0,
                                         forward=2,
                                         count=6)
    await callback.message.edit_text(text=f'Выберите пользователя, которого нужно удалить из {role}',
                                     reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('personal_del_forward'))
@error_handler
async def process_forward_del_admin(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_del_admin: {callback.message.chat.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    role = '<b>ПАРТНЕРОВ</b>'
    list_users: list[User] = await rq.get_users_role(role=edit_role)
    forward = int(callback.data.split('_')[-1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_del_personal(list_users=list_users,
                                         back=back,
                                         forward=forward,
                                         count=6)
    try:
        await callback.message.edit_text(text=f'Выберите пользователя, которого вы хотите удалить из {role}',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe пользоватeля, которого вы хотите удалить из {role}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_del_back_'))
@error_handler
async def process_back_del_admin(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей назад
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_back_del_admin: {callback.message.chat.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    role = '<b>ПАРТНЕРОВ</b>'
    list_users = await rq.get_users_role(role=edit_role)
    back = int(callback.data.split('_')[3]) - 1
    forward = back + 2
    keyboard = kb.keyboards_del_personal(list_users=list_users,
                                         back=back,
                                         forward=forward,
                                         count=6)
    try:
        await callback.message.edit_text(text=f'Выберите пользователя, которого вы хотите удалить из {role}',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe пользоватeля, которого вы хотите удалить из {role}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_del'))
@error_handler
async def process_delete_user(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение удаления
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_delete_user: {callback.message.chat.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    role = '<b>ПАРТНЕРОВ</b>'
    telegram_id = int(callback.data.split('_')[-1])
    user_info = await rq.get_user_tg_id(tg_id=telegram_id)
    await state.update_data(del_personal=telegram_id)
    await callback.message.edit_text(text=f'Удалить пользователя <a href="tg://user?id={user_info.tg_id}">'
                                          f'{user_info.username}</a> из {role}',
                                     reply_markup=kb.keyboard_del_list_personal())


@router.callback_query(F.data == 'not_del_personal_list')
@error_handler
async def process_not_del_personal_list(callback: CallbackQuery, bot: Bot) -> None:
    """
    Отмена изменения роли пользователя
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_not_del_personal_list: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.answer(text=f'Разжалование пользователя отменено', show_alert=True)
    await select_action_partner(message=callback.message, bot=bot)


@router.callback_query(F.data == 'del_personal_list')
@error_handler
async def process_del_personal_list(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_del_personal_list: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    data = await state.get_data()
    tg_id = data['del_personal']
    role = 'ПАРТНЕРОВ'
    await rq.update_user_role(tg_id=tg_id, role=rq.UserRole.user)
    await callback.answer(text=f'Пользователь успешно удален из {role}', show_alert=True)
    await bot.send_message(chat_id=tg_id,
                           text=f'Вы удалены из списка {role}',
                           reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await select_action_partner(message=callback.message, bot=bot)
