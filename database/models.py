from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


# Создаем асинхронный движок
engine = create_async_engine("sqlite+aiosqlite:///database/db.sqlite3", echo=False)
# Настраиваем фабрику сессий
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default='user')


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    frame_id: Mapped[int] = mapped_column(String)
    date_payment: Mapped[str] = mapped_column(String)
    link_folder: Mapped[str] = mapped_column(String)


class Frame(Base):
    __tablename__ = 'frames'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event: Mapped[str] = mapped_column(String)
    cost: Mapped[int] = mapped_column(Integer)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
