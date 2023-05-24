import os
import shutil

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from settings import UPLOAD_FILES_PATH
from tests.conftest import create_test_token, create_test_user, get_audios


async def test_post_audio(
        async_client: AsyncClient,
        db_session: AsyncSession,
        wav_file
):
    """
    Тестирование публикации аудио
    """

    user_1 = await create_test_user(db_session, username="user_1")
    user_2 = await create_test_user(db_session, username="user_2")
    # берем количество объектов Audio до добавления
    audios = await get_audios(db_session, all=True)
    count_audio_before_good_request = len(audios)

    token_user_1 = await create_test_token(user_id=str(user_1.id))

    response = await async_client.post(
        url="/record/",
        params={"user": str(user_2.id)},
        files={"file": ("filename", wav_file, "audio/wav")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )
    # отправляем еще один запрос с теми же данными
    response = await async_client.post(
        url="/record/",
        params={"user": str(user_2.id)},
        files={"file": ("filename", wav_file, "audio/wav")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )

    # берем количество объектов Audio после добавления
    audios = await get_audios(db_session, all=True)
    count_audio_after_good_request = len(audios)

    # берем последний элемент из Audio
    audio = await get_audios(db_session)

    # удаляем созданные файлы
    user_2_upload_path = os.path.join(UPLOAD_FILES_PATH, str(user_2.id))
    shutil.rmtree(user_2_upload_path)

    assert (count_audio_before_good_request + 2 ==
            count_audio_after_good_request)

    assert response.status_code == 201
    assert (response.json()["link"] ==
            f"http://test/record/?id={audio[0].id}&user={str(user_2.id)}")


async def test_bad_post_audio(
        async_client: AsyncClient,
        db_session: AsyncSession,
        wav_file
):
    """
    Тестирование плохих запросов при публикации аудио
    """

    user_1 = await create_test_user(db_session, username="user_1")
    bad_user_id = "a194defe-6f74-4d56-9835-67051d09d528"
    bad_token = "1234567"

    # берем количество объектов Audio до добавления
    audios = await get_audios(db_session, all=True)
    count_audio_before_bad_request = len(audios)

    token_user_1 = await create_test_token(user_id=str(user_1.id))

    # при неправильном user_id
    response_1 = await async_client.post(
        url="/record/",
        params={"user": bad_user_id},
        files={"file": ("filename", wav_file, "audio/wav")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )

    # при неверном формате файла
    response_2 = await async_client.post(
        url="/record/",
        params={"user": str(user_1.id)},
        files={"file": ("filename", wav_file, "audio/mp3")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )

    # при невалидном токене
    response_3 = await async_client.post(
        url="/record/",
        params={"user": str(user_1.id)},
        files={"file": ("filename", wav_file, "audio/mp3")},
        headers={"Authorization": f"Bearer {bad_token}"},
    )

    # берем количество объектов Audio после добавления
    audios = await get_audios(db_session, all=True)
    count_audio_after_bad_request = len(audios)

    assert response_1.status_code == 404
    assert response_2.status_code == 400
    assert response_3.status_code == 401
    assert count_audio_before_bad_request == count_audio_after_bad_request


async def test_get_audio(
        async_client: AsyncClient,
        db_session: AsyncSession,
        wav_file
):
    """
    Тестирование получения аудио
    """

    user_1 = await create_test_user(db_session, username="user_1")
    token_user_1 = await create_test_token(user_id=str(user_1.id))

    await async_client.post(
        url="/record/",
        params={"user": str(user_1.id)},
        files={"file": ("filename", wav_file, "audio/wav")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )

    audio = await get_audios(db_session)

    # до удаления файла из системы
    response_1 = await async_client.get(
        url="/record/",
        params={"id": str(audio[0].id), "user": str(user_1.id)},
    )

    user_2_upload_path = os.path.join(UPLOAD_FILES_PATH, str(user_1.id))
    shutil.rmtree(user_2_upload_path)

    # после удаления файла из системы
    response_2 = await async_client.get(
        url="/record/",
        params={"id": str(audio[0].id), "user": str(user_1.id)},
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 404


async def test_bad_get_audio(
        async_client: AsyncClient,
        db_session: AsyncSession,
        wav_file
):
    """
    Тестирование плохих запросов при получении аудио
    """

    user_1 = await create_test_user(db_session, username="user_1")
    token_user_1 = await create_test_token(user_id=str(user_1.id))
    bad_audio_id = "66f30e93-0b08-4137-8337-96ba859e95fe"
    bad_user_id = "66f30e93-0b08-4137-8337-96ba859e95fe"

    await async_client.post(
        url="/record/",
        params={"user": str(user_1.id)},
        files={"file": ("filename", wav_file, "audio/wav")},
        headers={"Authorization": f"Bearer {token_user_1}"},
    )
    audio = await get_audios(db_session)

    # запрос с неверным айди юзера
    response_1 = await async_client.get(
        url="/record/",
        params={"id": str(audio[0].id), "user": bad_user_id}
    )

    # запрос с неверным айди аудио
    response_2 = await async_client.get(
        url="/record/",
        params={"id": bad_audio_id, "user": str(user_1.id)}
    )

    user_2_upload_path = os.path.join(UPLOAD_FILES_PATH, str(user_1.id))
    shutil.rmtree(user_2_upload_path)

    assert response_1.status_code == 404
    assert response_2.status_code == 404
