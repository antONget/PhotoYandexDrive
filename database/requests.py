from database.models import async_session
from database.models import User, Order, Frame
from sqlalchemy import select
from dataclasses import dataclass
import logging


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
    logging.info(f'update_user_role')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
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


"""Order"""


async def add_order(data: dict) -> None:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(Order).where(Order.tg_id == data['tg_id']))

        session.add(Order(**data))
        await session.commit()


async def get_order_tg_id(tg_id: int) -> User:
    logging.info('get_user_tg_id')
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.tg_id == tg_id))


async def get_order_by_tg_id(tg_id: int) -> list[Order]:
    """
    Получение списка пользователей с заданной ролью
    :param tg_id:
    :return:
    """
    logging.info('get_order_by_tg_id')
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.tg_id == tg_id))
        if orders:
            list_users = [order for order in orders]
            return list_users
        else:
            return "0"


""" Frame """


async def get_frame_event(event: str) -> Frame:
    logging.info('get_frame_event')
    async with async_session() as session:
        return await session.scalar(select(Frame).where(Frame.event == event))


async def get_frame_id(id_: int) -> Frame:
    logging.info('get_frame_id')
    async with async_session() as session:
        return await session.scalar(select(Frame).where(Frame.id == id_))