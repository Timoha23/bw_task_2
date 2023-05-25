import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserCreate
from db.models import User


async def create_new_user(body: UserCreate, session: AsyncSession) -> User:
    """
    Создание юзера в БД
    """

    async with session.begin():
        user = User(
            username=body.username,
        )
        session.add(user)
        return user


async def get_user_by_uuid(
        user_id: uuid.UUID,
        session: AsyncSession
) -> User | None:
    """
    Получаем юзера по UUID
    """

    async with session.begin():
        query = select(User).where(User.id == user_id)
        res = await session.execute(query)
        user = res.fetchone()
        if user is not None:
            return user[0]
