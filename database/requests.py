from database.models import async_session
from database.models import User, Order, Frame, Token
from sqlalchemy import select, update
from dataclasses import dataclass
import logging
from datetime import datetime

"""USER"""


@dataclass
class UserRole:
    user = "user"
    partner = "partner"
    admin = "admin"


async def add_user(data: dict) -> None:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()
        else:
            user.username = data['username']
            await session.commit()


async def get_user_tg_id(tg_id: int) -> User:
    logging.info('get_user_tg_id')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_users_role(role: str) -> list[User]:
    """
    Получение списка пользователей с заданной ролью
    :param role:
    :return:
    """
    logging.info('get_users_role')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.role == role))
        list_users = [user for user in users]
        return list_users


async def update_username(tg_id: int, username: str) -> None:
    logging.info('update_username')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.username = username
        await session.commit()


async def update_link(tg_id: int, link: str) -> None:
    logging.info('update_invitation')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.link = link
        await session.commit()


async def get_user_username(username: str) -> User:
    logging.info('get_user_username')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.username == username))


async def update_user_role(tg_id: int, role: str) -> None:
    """
    Обновление роли пользователя
    :param tg_id:
    :param role:
    :return:
    """
    logging.info('set_user_phone')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.role = role
            await session.commit()


async def update_user_name(tg_id: int, name: str) -> None:
    logging.info(f'update_user_name')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.name = name
        await session.commit()


async def update_user_nickname(tg_id: int, nickname: str) -> None:
    logging.info(f'update_user_nickname')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.nickname = nickname
        await session.commit()


async def get_users() -> list[User]:
    logging.info('get_users')
    async with async_session() as session:
        users = await session.scalars(select(User))
        users_list = [user for user in users]
        return users_list


""" ORDER """


@dataclass
class StatusOrder:
    process = "process"
    payment = "payment"


async def add_order(data: dict) -> int:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        new_order = Order(**data)
        session.add(new_order)
        await session.flush()
        id_ = new_order.id
        await session.commit()
        return id_


async def get_orders_tg_id(tg_id: int) -> list[Order]:
    """
    Получение списка заказов пользователя
    :param tg_id:
    :return:
    """
    logging.info('get_order_tg_id')
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.tg_id == tg_id))
        return [order for order in orders]


async def get_order_id(id_: int) -> Order:
    """
    Получение заказа по id
    :param id_:
    :return:
    """
    logging.info('get_order_tg_id')
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == id_))


async def update_order_id(id_: int) -> None:
    """
    Обновление заказа по id
    :param id_:
    :return:
    """
    logging.info(f'update_order_id {id_}')
    async with async_session() as session:
        current_date = datetime.now()
        current_date_str = current_date.strftime('%d-%m-%Y %H:%M')
        await session.execute(update(Order).where(Order.id == id_).values(status_order=StatusOrder.payment,
                                                                          date_payment=current_date_str))
        await session.commit()


""" FRAME """


async def get_frame_event(event: str) -> Frame:
    logging.info('get_frame_event')
    async with async_session() as session:
        return await session.scalar(select(Frame).where(Frame.event == event))


async def get_frame_id(id_: int) -> Frame:
    logging.info('get_frame_id')
    async with async_session() as session:
        return await session.scalar(select(Frame).where(Frame.id == id_))


""" TOKEN """


async def add_token(data: dict) -> None:
    """
    Добавление токена
    :param data:
    :return:
    """
    logging.info(f'add_token')
    async with async_session() as session:
        new_token = Token(**data)
        session.add(new_token)
        await session.commit()


async def get_token(token: str, tg_id: int) -> bool | str:
    """
    Проверка валидности токена
    :param token:
    :param tg_id:
    :return:
    """
    logging.info('get_token')
    async with async_session() as session:
        token_ = await session.scalar(select(Token).filter(Token.token == token,
                                                           Token.tg_id == 0))
        if token_:
            token_.tg_id = tg_id
            role = token_.role
            await session.commit()
            return role
        else:
            return False