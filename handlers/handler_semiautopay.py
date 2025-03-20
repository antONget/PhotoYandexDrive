from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter


from keyboards.keyboard_semiautopay import keyboard_check_payment, keyboard_send_check, keyboard_show_orders
from keyboards.start_keyboard import keyboard_not_public_link, keyboard_wish
from config_data.config import Config, load_config
from database import requests as rq
from database.models import Frame, Order
from services.yandex_drive import get_photo_view_link
from utils.send_admins import send_text_admins
from datetime import datetime
import logging


router = Router()
config: Config = load_config()


class StateSemiAutoPay(StatesGroup):
    chek_pay = State()


@router.callback_query(F.data.startswith('semiautopay'))
async def process_select_item_semi_auto_pay(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор тарифа (товара) для оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_select_item_semi_auto_pay: {callback.message.chat.id}')
    data = await state.get_data()
    print(data)
    if data.get('msg_select', False):

        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=data['msg_select'])
        except:
            pass
    if data.get('msg_thanks', False):
        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=data['msg_thanks'])
        except:
            pass

    num_team = int(callback.data.split('!@!')[-1])
    frame_id = int(callback.data.split('!@!')[-2])
    cost = config.tg_bot.cost_default
    event = 'Событие'
    frame: Frame = await rq.get_frame_id(id_=frame_id)
    if frame:
        cost = frame.cost
        event = frame.event.split('/')[-1]
    path_event = f"disk:/MAIN/Ралли Яккима '25/preview/{num_team}"
    print(path_event, callback.from_user.id, num_team)
    order: Order = await rq.get_order_path(path=path_event,
                                           tg_id=callback.from_user.id,
                                           team=num_team)
    link_preview = await get_photo_view_link(file_path=path_event)
    await callback.message.edit_text(text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                          f'Стоимость вашего пакета {cost} ₽\n'
                                          f'посмотреть подборку:\n'
                                          f'{link_preview}\n\n'
                                          f'Ожидаем от Вас оплаты...',
                                     reply_markup=None)
    if data.get('msg_wish', False):
        try:
            # await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
            #                                     message_id=data['msg_wish'],
            #                                     reply_markup=keyboard_wish(id_frame=frame_id,
            #                                                                num_team=str(num_team)))
            await bot.edit_message_text(chat_id=callback.from_user.id,
                                        message_id=data['msg_wish'],
                                        text=f'<b>Ралли Яккима ‘25, экипаж {num_team}</b>\n'
                                             f'Стоимость вашего пакета {cost} ₽\n'
                                             f'посмотреть подборку:\n'
                                             f'{link_preview}\n\n'
                                             f'Ожидаем от Вас оплаты...',
                                        reply_markup=None)
        except:
            pass
    await state.set_state(state=None)
    await state.update_data(msg_wish=False)
    await state.update_data(msg_thanks=False)
    await state.update_data(msg=False)
    # frame_id = int(callback.data.split('!@!')[-2])
    await state.update_data(frame_id=frame_id)


    await callback.message.answer(text=f'Для оплаты\n'
                                       f'<b>{event}, экипаж {num_team}</b>\n'
                                       f'необходимо осуществить перевод\n'
                                       f' {cost} р. по номеру телефона:\n'
                                       f'+79817438193  или карты:\n'
                                       f'<code>2200 4002 0168 7437</code>\n'
                                       f'на имя: Ольга Ч, банк ВТБ\n'
                                       f'…и отправить нам чек.',
                                  reply_markup=keyboard_send_check(id_frame=frame_id))
    await callback.answer()


@router.callback_query(F.data.startswith('send_check_'))
async def process_get_check(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Запрос на отправку чека оплаты
    :param callback: send_check_{id_frame}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_check: {callback.message.chat.id}')
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text='отправьте скриншот чека сообщением')
    await state.update_data(id_frame=callback.data.split('_')[-1])
    await state.set_state(StateSemiAutoPay.chek_pay)
    await callback.answer()


@router.message(F.photo, StateFilter(StateSemiAutoPay.chek_pay))
async def get_check_payment(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Запрос на отправку чека оплаты
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_check_payment: {message.chat.id}')
    await message.answer(text='Данные отправлены на проверку администратору!')
    await state.set_state(state=None)
    data = await state.get_data()
    id_frame: str = data['id_frame']
    path = data['path']
    event = path.split('/')[-3]
    team = path.split('/')[-1]
    current_date = datetime.now()
    current_date_str = current_date.strftime('%d-%m-%Y %H:%M')
    data_order = {'tg_id': message.from_user.id,
                  'frame_id': int(id_frame),
                  'date_payment': current_date_str,
                  'team': team,
                  'event': event,
                  'path_folder': path,
                  'status_order': rq.StatusOrder.process}
    order_id: int = await rq.add_order(data=data_order)
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_photo(chat_id=admin,
                                 photo=message.photo[-1].file_id,
                                 caption=f'<a href="tg://user?id={message.from_user.id}">Пользователь</a> оплатил'
                                         f' подборку фотографий {event}/{team}. Подтвердите или отклоните оплату',
                                 reply_markup=keyboard_check_payment(order_id=order_id))
        except:
            pass


@router.callback_query(F.data.startswith('payment_'))
async def process_confirm_cancel_payment(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение или отклонение оплаты
    :param callback: payment_cancel_{order_id} | payment_confirm_{order_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_confirm_cancel_payment: {callback.message.chat.id}')
    payment: str = callback.data.split('_')[-2]
    order_id: int = int(callback.data.split('_')[-1])
    info_order: Order = await rq.get_order_id(id_=order_id)
    path = info_order.path_folder
    event = path.split('/')[-3]
    team = path.split('/')[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
    if payment == 'cancel':
        await callback.message.answer(text='Платеж отклонен')
        await bot.send_message(chat_id=info_order.tg_id,
                               text='Ваш платеж отклонен!',
                               reply_markup=keyboard_not_public_link())
    elif payment == 'confirm':
        link_original = await get_photo_view_link(file_path=path.replace('preview', 'original'))
        if link_original:
            await callback.message.answer(text=f'<a href="tg://user?id={info_order.tg_id}">Пользователю</a>'
                                               f' открыт доступ к оригинальным фотографиям события'
                                               f' {event}: команда {team} ')
            current_date = datetime.now()
            current_date_str = current_date.strftime('%d.%m.%Y %H:%M')
            await bot.send_message(chat_id=info_order.tg_id,
                                   text=f'<b>Ралли Яккима ‘25, экипаж {team}</b>\n'
                                        f'покупка от: {current_date_str}\n'
                                        f'{link_original}')
            msg = await bot.send_message(chat_id=info_order.tg_id,
                                         text='Благодарим вас за покупку, можете посмотреть другие подборки',
                                         reply_markup=keyboard_not_public_link())
            await state.update_data(msg=msg)
        else:
            await bot.send_message(chat_id=info_order.tg_id,
                                   text='Фотографии для вашего экипажа ещё не добавлены, как они будут'
                                        ' загружены мы вас оповестим.',
                                   reply_markup=keyboard_not_public_link())
            await send_text_admins(bot=bot,
                                   text=f'Пользователь <a href="tg://user?id={info_order.tg_id}">'
                                        f'{callback.from_user.username}</a> оплатил подборку фотографий '
                                        f'<b>{event} экипаж {team}</b> но  ссылку не получил')
        await rq.update_order_id(id_=order_id)
    await callback.answer()
