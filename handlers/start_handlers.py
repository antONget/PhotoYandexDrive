from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import requests as rq
from database.requests import add_user
from utils.error_handling import error_handler
from services.yandex_drive import get_list_folders_to_path, get_download_link, get_photo_view_link
from filter.admin_filter import check_super_admin
from utils.utils_keyboard import utils_handler_pagination_and_select_item
from keyboards.start_keyboard import keyboard_preview_folder, keyboard_start
import logging
from config_data.config import Config, load_config

router = Router()
router.message.filter(F.chat.type == "private")


# Определение состояний
class Registration(StatesGroup):
    name = State()
    age = State()


@router.message(CommandStart())
@error_handler
async def process_press_start(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработка нажатия на кнопку старт и вывод списка события
    :param message:
    :param state:
    :param bot:
    :return:
    """
    config: Config = load_config()
    logging.info('process_press_start ')
    tg_id: int = message.from_user.id
    username: str = message.from_user.username
    data = {"tg_id": tg_id, "username": username}
    if await check_super_admin(telegram_id=message.from_user.id):
        data = {"tg_id": tg_id, "username": username, "role": rq.UserRole.admin}
    await add_user(data)
    path = "disk:/MAIN/Ралли Яккима '25"
    await state.update_data(path=path)
    # user = await rq.get_user_tg_id(tg_id)
    # if user.role == rq.UserRole.admin or tg_id == config.tg_bot.admin_ids:
    #     # await message.answer(text="Вы являетесь администратором этого бота",
    #     #                      reply_markup=keyboard_start(rq.UserRole.admin))
    #     data = {"tg_id": tg_id, "username": username, "role": rq.UserRole.admin}
    # else:
    #     await message.answer(text="Вы находитесь в главном меню", reply_markup=keyboard_start(rq.UserRole.user))

# @router.message(F.text == "Создать заказ")
# async def create_order(message: Message, state: FSMContext, bot: Bot) -> None:
#         list_file = await get_list_folders_to_path("disk:/MAIN/")
#         if list_file:
#             await utils_handler_pagination_and_select_item(list_items=list_file,
#                                                            text_message_pagination=
#                                                            'Выберите событие для которого вы бы хотели бы приобрести подборку фотографий:',
#                                                            page=0,
#                                                            count_item_page=100,
#                                                            callback_prefix_select='event_select',
#                                                            callback_prefix_back='event_back',
#                                                            callback_prefix_next='event_next',
#                                                            callback=None,
#                                                            message=message)
#         else:
#             await message.answer(text='Нет событий для выбора')
#
#
# @router.callback_query(F.data.startswith('event_back'))
# @router.callback_query(F.data.startswith('event_next'))
# async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Пагинация списка
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info('process_press_start ')
#     page = int(callback.data.split('_')[-1])
#     data = await state.get_data()
#     path = data['path']
#     list_file = await get_list_folders_to_path(path)
#     await utils_handler_pagination_and_select_item(list_items=list_file,
#                                                    text_message_pagination='Выберите событие:',
#                                                    page=page,
#                                                    count_item_page=100,
#                                                    callback_prefix_select='event_select',
#                                                    callback_prefix_back='event_back',
#                                                    callback_prefix_next='event_next',
#                                                    callback=callback,
#                                                    message=None)
#
#
# @router.callback_query(F.data.startswith('event_select_'))
# async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Выбор события и отображение участвующих команд
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     data = await state.get_data()
#     path = data['path']
#     path = path + callback.data.split('_')[-1]
    list_file = await get_list_folders_to_path(path)
    if list_file:
        if 'preview' in list_file:
            path = path + '/preview'
            list_folder = await get_list_folders_to_path(path)
            list_folder_int = list(map(int, list_folder))
            list_sorted = sorted(list_folder_int)
            list_file = list(map(str, list_sorted))
        await state.update_data(path=path)
        await utils_handler_pagination_and_select_item(list_items=list_file,
                                                       text_message_pagination='Выберите команду:',
                                                       page=0,
                                                       count_item_page=100,
                                                       callback_prefix_select='team_select',
                                                       callback_prefix_back='team_back',
                                                       callback_prefix_next='team_next',
                                                       callback=None,
                                                       message=message)
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
    path = path + '/' + callback.data.split('_')[-1]
    await state.update_data(path=path)
    frame = await rq.get_frame_event(event=path.split('/')[-3])
    cost = 3000
    id_frame = 0
    if frame:
        cost = frame.cost
        id_frame = frame.id
    link_preview = await get_photo_view_link(file_path=path)
    await callback.message.edit_text(text=f'Посмотреть подборку можно здесь\n\n'
                                          f'{link_preview},'
                                          f' стоимость вашего пакета {cost} ₽',
                                     reply_markup=keyboard_preview_folder(id_frame=id_frame))


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
    list_file = await get_list_folders_to_path(path_event)
    await state.update_data(path=path_event)
    if list_file:
        await utils_handler_pagination_and_select_item(list_items=list_file,
                                                       text_message_pagination='Выберите пожалуйста команду:',
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
    tg_id: int = callback.from_user.id
    username: str = callback.from_user.username
    data = {"tg_id": tg_id, "username": username}
    if await check_super_admin(telegram_id=callback.from_user.id):
        data = {"tg_id": tg_id, "username": username, "role": rq.UserRole.admin}
    await add_user(data)
    list_file = await get_list_folders_to_path("disk:/MAIN/")
    await state.update_data(path="disk:/MAIN/")
    if list_file:
        await utils_handler_pagination_and_select_item(list_items=list_file,
                                                       text_message_pagination=
                                                       'Выберите событие для которого вы бы хотели бы приобрести подборку фотографий:',
                                                       page=0,
                                                       count_item_page=100,
                                                       callback_prefix_select='event_select',
                                                       callback_prefix_back='event_back',
                                                       callback_prefix_next='event_next',
                                                       callback=callback,
                                                       message=None)
    else:
        await callback.answer(text='Нет событий для выбора')