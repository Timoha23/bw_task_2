from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


async def test_register(
        async_client: AsyncClient,
        db_session: AsyncSession
):
    """
    Тестирование регистрации пользователя
    """

    async with db_session.begin():
        query = select(User)
        res = await db_session.execute(query)
        users = res.fetchall()

    count_users_before_good_request = len(users)

    user_data = {"username": "Ivan1234"}

    response = await async_client.post("/user/", json=user_data)

    # проверяем что юзер создался
    async with db_session.begin():
        query = select(User)
        res = await db_session.execute(query)
        users = res.fetchall()

    # проверяем что вернулся корректный ответ
    async with db_session.begin():
        query = select(User).where(User.username == user_data["username"])
        res = await db_session.execute(query)
        user = res.fetchone()[0]

    count_users_after_good_request = len(users)
    assert (count_users_before_good_request + 1 ==
            count_users_after_good_request)

    assert response.json()["user_id"] == str(user.id)
    assert response.json().get("token") is not None
    assert response.status_code == 201


async def test_bad_register(
        async_client: AsyncClient,
        db_session: AsyncSession
):
    """
    Тестирование плохих запросов при регистрации юзера
    """

    async with db_session.begin():
        query = select(User)
        res = await db_session.execute(query)
        users = res.fetchall()

    count_users_before_bad_request = len(users)

    user_data = {"username": "Ivan"}
    response = await async_client.post(url="/user/", json=user_data)
    assert response.status_code == 422

    user_data = {"username": "Ivan@%^^*!"}
    response = await async_client.post(url="/user/", json=user_data)
    assert response.status_code == 422

    user_data = {"username": "I" * 30}
    response = await async_client.post(url="/user/", json=user_data)
    assert response.status_code == 422

    async with db_session.begin():
        query = select(User)
        res = await db_session.execute(query)
        users = res.fetchall()
    count_users_after_bad_reqeust = len(users)

    assert count_users_before_bad_request == count_users_after_bad_reqeust
