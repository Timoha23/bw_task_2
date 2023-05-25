import asyncio
import os
from typing import Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Audio, Base, User
from db.session import get_db
from main import app
from security import create_access_token
from settings import TEST_DATABASE_URL
from tests.wav_generator import create_wav


engine_test = create_async_engine(TEST_DATABASE_URL)

async_session_test = sessionmaker(
    engine_test,
    expire_on_commit=False,
    class_=AsyncSession
)

metadata = Base.metadata
metadata.bind = engine_test


async def _get_db_test() -> Generator:
    try:
        session: AsyncSession = async_session_test()
        yield session
    finally:
        await session.close()


app.dependency_overrides[get_db] = _get_db_test


@pytest.fixture(autouse=True, scope="session")
async def prepate_databse():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def db_session() -> Generator:
    try:
        session: AsyncSession = async_session_test()
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="session")
async def wav_file():
    wav_file_path = create_wav()
    with open(wav_file_path, "rb") as wav_file:
        yield wav_file
    os.remove(wav_file_path)


async def create_test_token(user_id: str) -> str:
    data = {"sub": user_id}
    access_token = create_access_token(data=data)
    return access_token


async def get_audios(
        db_session: AsyncSession,
        all: bool = False
) -> Audio | list[Audio]:

    async with db_session.begin():
        query = select(Audio)
        res = await db_session.execute(query)
        if all:
            return res.fetchall()
        return res.fetchall()[-1]


async def create_test_user(db_session: AsyncSession, username: str) -> User:
    async with db_session.begin():
        user = User(
            username=username
        )
        db_session.add(user)
        await db_session.commit()
        return user
