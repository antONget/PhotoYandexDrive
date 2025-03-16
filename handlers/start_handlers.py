from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext

from database import requests as rq
from database.requests import add_user
from utils.error_handling import error_handler
from services.yandex_drive import get_list_folders_to_path, get_list_file_to_path, get_photo_view_link
from filter.admin_filter import check_super_admin
from utils.utils_keyboard import utils_handler_pagination_and_select_item
from utils.send_admins import send_text_admins
from filter.user_filter import check_role
from keyboards.start_keyboard import keyboard_preview_folder, keyboard_start, keyboard_not_public_link, keyboard_wish
import logging
from config_data.config import Config, load_config
from handlers.command_handler import command_orders, command_help, command_support

router = Router()
router.message.filter(F.chat.type == "private")
config: Config = load_config()


class SelectTeam(StatesGroup):
    team = State()


async def registration(message: Message, state: FSMContext, command: CommandObject, bot: Bot):
    logging.info('registration')
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
    await registration(message=message, state=state, command=command, bot=bot)
    path_root = "disk:/MAIN"
    event = "Ралли Яккима '25"
    path = f"{path_root}/{event}"
    await state.update_data(path=path)
    list_folder = await get_list_folders_to_path(path)
    if list_folder:
        if 'preview' in list_folder:
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
            msg = await utils_handler_pagination_and_select_item(list_items=list_file,
                                                                 text_message_pagination="<b>Ралли Яккима '25</b>\n"
                                                                                         "Выберите номер экипажа\n"
                                                                                         "…или отправьте сообщением!",
                                                                 page=0,
                                                                 count_item_page=100,
                                                                 callback_prefix_select='team_select',
                                                                 callback_prefix_back='team_back',
                                                                 callback_prefix_next='team_next',
                                                                 callback=None,
                                                                 message=message)
            await state.update_data(msg_select=msg.message_id)
            await state.set_state(SelectTeam.team)
        else:
            await message.answer('preview')
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
    msg = await utils_handler_pagination_and_select_item(list_items=list_file,
                                                         text_message_pagination='Выберите событие:',
                                                         page=page,
                                                         count_item_page=100,
                                                         callback_prefix_select='team_select',
                                                         callback_prefix_back='team_back',
                                                         callback_prefix_next='team_next',
                                                         callback=callback,
                                                         message=None)
    await state.update_data(msg_select=msg.message_id)


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
    logging.info(f'get_team {message.message_id}')
    # если пользователь ввел команду
    if message.text == '/order':
        await command_orders(message=message, bot=bot)
        return
    if message.text == '/help':
        await command_help(message=message, bot=bot)
        return
    if message.text == '/support':
        await command_support(message=message, bot=bot)
        return
    # выполняем действие в зависимости из какой цепочки пришли
    data = await state.get_data()
    # удаляем клавиатуру, оставляем сообщение
    if data.get('msg', False):
        print('msg', data.get('msg', False))
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=data.get('msg', False),
                                            reply_markup=None)
        await state.update_data(msg=False)
    # заменяем клавиатуру на 'Хочу приобрести эти фото'
    elif data.get('msg_wish', False):
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=data['msg_wish'],
                                            reply_markup=keyboard_wish(id_frame=data['id_frame'],
                                                                       num_team=data['num_team_wish']))
        await state.update_data(msg_wish=False)
    # удаляем сообщение если пришли из цепочки 'спасибо, не в этот раз'
    elif data.get('msg_thanks', False):
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=data['msg_thanks'])
        await state.update_data(msg_thanks=False)
    # если не одна из этих цепочек, то просто удаляем
    else:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=message.message_id - 1)

    num_team = message.text
    path = "disk:/MAIN/Ралли Яккима '25"
    if await check_role(tg_id=message.from_user.id,
                        role=rq.UserRole.partner) or await check_role(tg_id=message.from_user.id,
                                                                      role=rq.UserRole.admin):
        path = path + '/original'
    else:
        path = path + '/preview'
    list_folder = await get_list_folders_to_path(path)
    list_folder_int = list(map(int, list_folder))
    # проверка того что введенное значение число и оно есть в списке папок
    if num_team.isdigit() and int(num_team) in list_folder_int:
        await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
        path = path + '/' + str(int(num_team))
        path_team = path
        list_file = await get_list_file_to_path(path=path)
        await state.update_data(path=path)
        event = path.split('/')[-2]
        # если файлы в папке есть
        if list_file:
            # данные о тарифе для папки
            frame = await rq.get_frame_event(event="disk:/MAIN/Ралли Яккима '25")
            cost = int(config.tg_bot.cost_default)
            id_frame = 0
            if frame:
                cost = frame.cost
                id_frame = frame.id
                print(cost, id_frame)
            await state.update_data(id_frame=id_frame)
            # получаем ссылку
            link_preview = await get_photo_view_link(file_path=path)
            # если ссылка сформирована успешно
            if link_preview:
                # для партнера и админа сразу выводим оригиналы
                if await check_role(tg_id=message.from_user.id,
                                    role=rq.UserRole.partner) or await check_role(tg_id=message.from_user.id,
                                                                                  role=rq.UserRole.admin):
                    await message.answer(text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                              f'посмотреть подборку:\n'
                                              f'{link_preview}',
                                         reply_markup=keyboard_not_public_link())
                # для пользователя предлагаем посмотреть превью
                else:
                    msg = await message.answer(text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                                    f'Стоимость вашего пакета {cost} ₽\n'
                                                    f'посмотреть подборку:\n'
                                                    f'{link_preview}',
                                               reply_markup=keyboard_preview_folder(id_frame=id_frame,
                                                                                    num_team=num_team))
                    await state.update_data(msg_wish=msg.message_id)
                    await state.update_data(num_team_wish=num_team)
            # если возникла проблема при формировании ссылки
            else:
                msg = await message.answer(text='Возникла проблема с генерацией ссылки на подборку фотографий',
                                           reply_markup=keyboard_not_public_link())
                await send_text_admins(bot=bot,
                                       text=f'При генерации ссылки на подборку фотографий <b>{event}'
                                            f' экипаж {num_team}</b>'
                                            f'у пользователя <a href="tg://user?id={message.from_user.id}">'
                                            f'{message.from_user.username}</a> возникла проблема')
                await state.update_data(msg=msg.message_id)
        # файлов в папке нет
        else:
            msg = await message.answer(text='Фотографии для вашего экипажа ещё не добавлены, как они будут'
                                            ' загружены мы вас оповестим.',
                                       reply_markup=keyboard_not_public_link())
            await state.update_data(msg=msg.message_id)
            await send_text_admins(bot=bot,
                                   text=f'Пользователь <a href="tg://user?id={message.from_user.id}">'
                                        f'{message.from_user.username}</a> заинтересовался подборкой фотографий '
                                        f'<b>{event} экипаж {num_team}</b>')
    # не корректно указан номер экипажа
    else:
        msg_not_team = await message.answer(text='Такой экипаж не найден!',
                                            reply_markup=keyboard_not_public_link())
        await state.update_data(msg=msg_not_team.message_id)
        await state.update_data(msg_wish=False)
        await state.update_data(not_team=True)


@router.callback_query(F.data.startswith('team_select_'))
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор команды через клавиатуру
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_team_select')
    await callback.message.delete()
    data = await state.get_data()
    path = data['path']
    num_team = callback.data.split('_')[-1]
    path = path + '/' + num_team
    await state.update_data(path=path)
    list_file = await get_list_file_to_path(path=path)
    event = path.split('/')[-2]
    path_team = path
    print(path)
    frame = await rq.get_frame_event(event="disk:/MAIN/Ралли Яккима '25")
    cost = config.tg_bot.cost_default
    id_frame = 0
    if frame:
        cost = frame.cost
        id_frame = frame.id
    await state.update_data(id_frame=id_frame)
    await bot.send_chat_action(chat_id=callback.from_user.id, action='typing')
    await bot.send_message(chat_id=callback.from_user.id, text=num_team)
    if list_file:
        link_preview = await get_photo_view_link(file_path=path)
        if link_preview:
            if await check_role(tg_id=callback.from_user.id,
                                role=rq.UserRole.partner) or await check_role(tg_id=callback.from_user.id,
                                                                              role=rq.UserRole.admin):
                await callback.message.answer(text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                                   f'посмотреть подборку:\n'
                                                   f'{link_preview}',
                                              reply_markup=keyboard_not_public_link())
            else:
                print(id_frame, num_team)
                msg = await callback.message.answer(text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                                         f'Стоимость вашего пакета {cost} ₽\n'
                                                         f'посмотреть подборку:\n'
                                                         f'{link_preview}',
                                                    reply_markup=keyboard_preview_folder(id_frame=id_frame,
                                                                                         num_team=num_team))
                await state.update_data(msg_wish=msg.message_id)
                await state.update_data(num_team_wish=num_team)
        else:
            msg = await callback.message.answer(text='Возникла проблема с генерацией ссылки на подборку фотографий',
                                                reply_markup=keyboard_not_public_link())
            await send_text_admins(bot=bot,
                                   text=f'При генерации ссылки на подборку фотографий <b>{event} экипаж {num_team}</b>'
                                        f'у пользователя <a href="tg://user?id={callback.from_user.id}">'
                                        f'{callback.from_user.username}</a> возникла проблема')
            await state.update_data(msg=msg.message_id)
    else:
        msg = await callback.message.answer(text='Фотографии для вашего экипажа ещё не добавлены, как они будут'
                                                 ' загружены мы вас оповестим.',
                                            reply_markup=keyboard_not_public_link())
        await state.update_data(msg=msg.message_id)
        await send_text_admins(bot=bot,
                               text=f'Пользователь <a href="tg://user?id={callback.from_user.id}">'
                                    f'{callback.from_user.username}</a> заинтересовался подборкой фотографий '
                                    f'<b>{event} экипаж {num_team}</b>')


@router.callback_query(F.data.startswith('other_team'))
async def process_select_other_team(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор команды
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_select_other_team')
    data = await state.get_data()
    print(data)
    await state.update_data(msg=False)
    if data.get('msg_wish', False):
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=data['msg_wish'],
                                            reply_markup=keyboard_wish(id_frame=data['id_frame'],
                                                                       num_team=data['num_team_wish']))
        await state.update_data(msg_wish=False)
        await state.update_data(num_team_wish=False)
    elif data.get('msg_thanks', False):
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=data['msg_thanks'])
        await state.update_data(msg_thanks=False)
    else:
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=None)

    # path_list = data['path'].split('/')
    # path_event = '/'.join(path_list[:-1])
    # if data.get('not_team', False):
    #     path_event = '/'.join(path_list[:])
    #     await state.update_data(not_team=False)
    # print(path_event, data.get('not_team', False))
    path_event = "disk:/MAIN/Ралли Яккима '25"
    if await check_role(tg_id=callback.from_user.id,
                        role=rq.UserRole.partner) or await check_role(tg_id=callback.from_user.id,
                                                                      role=rq.UserRole.admin):
        path_event = path_event + '/original'
    else:
        path_event = path_event + '/preview'
    list_folder = await get_list_folders_to_path(path=path_event)
    if list_folder:
        list_folder_int = list(map(int, list_folder))
        list_sorted = sorted(list_folder_int)
        list_file = list(map(str, list_sorted))
        await state.update_data(path=path_event)
        msg = await utils_handler_pagination_and_select_item(list_items=list_file,
                                                             text_message_pagination="<b>Ралли Яккима '25</b>\n"
                                                                                     "Выберите номер экипажа\n"
                                                                                     "…или отправьте сообщением!",
                                                             page=0,
                                                             count_item_page=100,
                                                             callback_prefix_select='team_select',
                                                             callback_prefix_back='team_back',
                                                             callback_prefix_next='team_next',
                                                             callback=callback,
                                                             message=None)
        await state.update_data(msg_select=msg.message_id)
        await state.set_state(SelectTeam.team)
    else:
        await callback.message.answer(text='Нет команд для выбора')
    await callback.answer()


@router.callback_query(F.data == 'cancel')
async def process_select_cancel(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Возврат в начало бота
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_select_cancel')
    data = await state.get_data()
    if data.get('msg_wish', False):
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=data['msg_wish'],
                                            reply_markup=keyboard_wish(id_frame=data['id_frame'],
                                                                       num_team=data['num_team_wish']))
        await state.update_data(msg_wish=False)
    else:
        await callback.message.edit_reply_markup(reply_markup=None)
    msg = await callback.message.answer(text='Благодарим за интерес к нашему проекту, будем рады видеть вас снова!',
                                        reply_markup=keyboard_not_public_link())
    await state.update_data(msg_thanks=msg.message_id)
    await send_text_admins(bot=bot,
                           text=f'Пользователь <a href="tg://user?id={callback.from_user.id}">'
                                f'{callback.from_user.username}</a>, отказался от покупки')
    await state.update_data(msg_wish=False)
    await callback.answer()
