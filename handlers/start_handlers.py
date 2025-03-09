from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext

from database import requests as rq
from database.requests import add_user
from utils.error_handling import error_handler
from services.yandex_drive import get_list_folders_to_path, get_download_link, get_photo_view_link
from filter.admin_filter import check_super_admin
from utils.utils_keyboard import utils_handler_pagination_and_select_item
from utils.send_admins import send_text_admins
from filter.user_filter import check_role
from keyboards.start_keyboard import keyboard_preview_folder, keyboard_start, keyboard_not_public_link
import logging
from config_data.config import Config, load_config

router = Router()
router.message.filter(F.chat.type == "private")
config: Config = load_config()


class SelectTeam(StatesGroup):
    team = State()


@router.message(CommandStart())
@error_handler
async def process_press_start(message: Message, state: FSMContext, command: CommandObject, bot: Bot) -> None:
    """
    Обработка нажатия на кнопку старт и вывод списка события
    :param message:
    :param state:
    :param command:
    :param bot:
    :return:
    """
    logging.info('process_press_start ')
    token = command.args
    tg_id: int = message.from_user.id
    username: str = message.from_user.username
    data = {"tg_id": tg_id, "username": username}
    if await check_super_admin(telegram_id=message.from_user.id):
        data = {"tg_id": tg_id, "username": username, "role": rq.UserRole.admin}
        await message.answer(text='Вы АДМИНИСТРАТОР проекта',
                             reply_markup=keyboard_start())
    await add_user(data)
    if token:
        role = await rq.get_token(token=token, tg_id=message.from_user.id)
        if role:
            await rq.update_user_role(tg_id=message.from_user.id,
                                      role=role)
        else:
            await message.answer(text='Пригласительная ссылка не валидна')
    path = "disk:/MAIN/Ралли Яккима '25"
    await state.update_data(path=path)
    list_file = await get_list_folders_to_path(path)
    if list_file:
        if 'preview' in list_file:
            if await check_role(tg_id=message.from_user.id,
                                role=rq.UserRole.partner) or await check_role(tg_id=message.from_user.id,
                                                                              role=rq.UserRole.admin):
                path = path + '/original'
            else:
                path = path + '/preview'
            list_folder = await get_list_folders_to_path(path)
            list_folder_int = list(map(int, list_folder))
            list_sorted = sorted(list_folder_int)
            list_file = list(map(str, list_sorted))
        await state.update_data(path=path)
        await utils_handler_pagination_and_select_item(list_items=list_file,
                                                       text_message_pagination="Событие: <b>Ралли Яккима '25</b>\n"
                                                                               "Выберите номер экипажа или"
                                                                               " отправьте сообщением!",
                                                       page=0,
                                                       count_item_page=100,
                                                       callback_prefix_select='team_select',
                                                       callback_prefix_back='team_back',
                                                       callback_prefix_next='team_next',
                                                       callback=None,
                                                       message=message)
        await state.set_state(SelectTeam.team)
    else:
        await message.edit_text(text='Нет команд для выбора')


@router.callback_query(F.data.startswith('team_back'))
@router.callback_query(F.data.startswith('team_next'))
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация списка
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_press_start ')
    page = int(callback.data.split('_')[-1])
    data = await state.get_data()
    path = data['path']
    list_folder = await get_list_folders_to_path(path)
    list_folder_int = list(map(int, list_folder))
    list_sorted = sorted(list_folder_int)
    list_file = list(map(str, list_sorted))
    await utils_handler_pagination_and_select_item(list_items=list_file,
                                                   text_message_pagination='Выберите событие:',
                                                   page=page,
                                                   count_item_page=100,
                                                   callback_prefix_select='team_select',
                                                   callback_prefix_back='team_back',
                                                   callback_prefix_next='team_next',
                                                   callback=callback,
                                                   message=None)


@router.message(F.text, StateFilter(SelectTeam.team))
@error_handler
async def get_team(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем номер экипажа от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_team')
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id-1)
    except:
        pass
    num_team = message.text
    data = await state.get_data()
    path = data['path']
    list_folder = await get_list_folders_to_path(path)
    list_folder_int = list(map(int, list_folder))
    if num_team.isdigit() and int(num_team) in list_folder_int:
        path = path + '/' + str(int(num_team))
        await state.update_data(path=path)
        event = path.split('/')[-3]
        frame = await rq.get_frame_event(event=event)
        cost = int(config.tg_bot.cost_default)
        id_frame = 0
        if frame:
            cost = frame.cost
            id_frame = frame.id
        link_preview = await get_photo_view_link(file_path=path)
        if link_preview:
            if check_role(tg_id=message.from_user.id,
                          role=rq.UserRole.partner) or check_role(tg_id=message.from_user.id,
                                                                  role=rq.UserRole.admin):
                await message.answer(text=f'Посмотреть подборку оригиналов фотографий можно здесь\n\n'
                                          f'{link_preview}')
            else:
                await message.answer(text=f'Посмотреть подборку можно здесь\n\n'
                                          f'{link_preview},'
                                          f' стоимость вашего пакета {cost} ₽',
                                     reply_markup=keyboard_preview_folder(id_frame=id_frame))
        else:
            await message.answer(text='Фотографии для вашего экипажа ещё не добавлены, как они будут'
                                      ' загружены мы вас оповестить.')
            await send_text_admins(bot=bot,
                                   text=f'Пользователь <a href="tg://userid?id={message.from_user.id}">'
                                        f'{message.from_user.username}</a> заинтересовался подборкой фотографий '
                                        f'<b>{event} экипаж {num_team}</b>')
        await state.set_state(state=None)
    else:
        await message.answer(text='Такой экипаж не найден')


@router.callback_query(F.data.startswith('team_select_'))
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор команды
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    data = await state.get_data()
    path = data['path']
    num_team = callback.data.split('_')[-1]
    path = path + '/' + num_team
    await state.update_data(path=path)
    event = path.split('/')[-3]
    frame = await rq.get_frame_event(event=event)
    cost = config.tg_bot.cost_default
    id_frame = 0
    if frame:
        cost = frame.cost
        id_frame = frame.id
    link_preview = await get_photo_view_link(file_path=path)
    if link_preview:
        if await check_role(tg_id=callback.from_user.id,
                            role=rq.UserRole.partner) or await check_role(tg_id=callback.from_user.id,
                                                                          role=rq.UserRole.admin):
            await callback.message.edit_text(text=f'Посмотреть подборку оригиналов фотографий можно здесь\n\n'
                                                  f'{link_preview}')
        else:
            await callback.message.edit_text(text=f'Посмотреть подборку можно здесь\n\n'
                                                  f'{link_preview},'
                                                  f' стоимость вашего пакета {cost} ₽',
                                             reply_markup=keyboard_preview_folder(id_frame=id_frame))
    else:
        await callback.message.edit_text(text='Фотографии для вашего экипажа ещё не добавлены, как они будут'
                                              ' загружены мы вас оповестим.',
                                         reply_markup=keyboard_not_public_link())
        await send_text_admins(bot=bot,
                               text=f'Пользователь <a href="tg://userid?id={callback.from_user.id}">'
                                    f'{callback.from_user.username}</a> заинтересовался подборкой фотографий '
                                    f'<b>{event} экипаж {num_team}</b>')


@router.callback_query(F.data.startswith('other_team'))
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор команды
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    data = await state.get_data()
    path_list = data['path'].split('/')
    path_event = '/'.join(path_list[:-1])
    if await check_role(tg_id=callback.from_user.id,
                        role=rq.UserRole.partner) or await check_role(tg_id=callback.from_user.id,
                                                                      role=rq.UserRole.admin):
        path_event = path_event + '/original'
    list_folder = await get_list_folders_to_path(path_event)
    if list_folder:
        list_folder_int = list(map(int, list_folder))
        list_sorted = sorted(list_folder_int)
        list_file = list(map(str, list_sorted))
        await state.update_data(path=path_event)
        await utils_handler_pagination_and_select_item(list_items=list_file,
                                                       text_message_pagination="Событие: <b>Ралли Яккима '25</b>\n"
                                                                               "Выберите номер экипажа или"
                                                                               " отправьте сообщением!",
                                                       page=0,
                                                       count_item_page=100,
                                                       callback_prefix_select='team_select',
                                                       callback_prefix_back='team_back',
                                                       callback_prefix_next='team_next',
                                                       callback=callback,
                                                       message=None)
    else:
        await callback.message.edit_text(text='Нет команд для выбора')
    await callback.answer()


@router.callback_query(F.data == 'cancel')
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Возврат в начало бота
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    await state.clear()
    await callback.message.answer(text='Благодарим за интерес к нашему проекту, будем рады видеть вас снова!')
    await callback.answer()
