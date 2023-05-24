import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.audio import (convert_from_wav_to_mp3,
                               get_audio_file_by_id_and_user_id,
                               upload_audio_file)
from api.actions.auth import get_current_user
from api.actions.users import get_user_by_uuid
from api.schemas import GetAudio
from db.models import User
from db.session import get_db
from settings import UPLOAD_FILES_PATH

audio_router = APIRouter()


@audio_router.post("/", status_code=201)
async def post_audio(
    user: uuid.UUID,
    file: UploadFile,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> GetAudio:
    """
    Добавление аудиозаписи
    """

    user_obj = await get_user_by_uuid(user, session)
    # если юзер с данным uuid не найден райзим исключение
    if user_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с id {user} не найден"
        )

    if file.content_type != "audio/wav":
        raise HTTPException(
            status_code=400,
            detail="Принимаемый формат файла .wav"
        )
    size_mb = round(file.size / 1024**2, 7)
    if size_mb > 50:
        raise HTTPException(
            status_code=400,
            detail="Размер файла не должен превышать 50 мегабайт"
        )

    upload_path = f"{UPLOAD_FILES_PATH}/{user}"
    # если данной директории нет, то создаем новую
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    full_path = f"{upload_path}/{file.filename}"

    # проверяем существует ли файл с данным именем. Если да,
    # то присваиваем новое имя содержащее номер
    counter = 0
    while True:
        if counter == 0:
            new_file_name = file.filename.split(".wav")[0] + ".mp3"
        else:
            new_file_name = (
                file.filename.split(".wav")[0] + f"({counter})" + ".mp3"
            )
        full_path_mp3 = f"{upload_path}/{new_file_name}"
        check = os.path.exists(full_path_mp3)
        if check:
            counter += 1
        else:
            file.filename = new_file_name.split(".mp3")[0] + ".wav"
            full_path = full_path_mp3.split(".mp3")[0] + ".wav"
            break

    # сохраняем файл
    with open(full_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # конвертируем файл
    filename = await convert_from_wav_to_mp3(upload_path, file.filename)

    # создаем объект в БД
    audio = await upload_audio_file(
        filename=filename,
        user_id=user,
        owner_id=current_user.id,
        session=session
    )

    # возвращаем ссылку на скачивание
    load_url = (
        f"{str(request.url).split('?')[0]}?id={audio.id}&user={user}"
    )

    return GetAudio(
        link=load_url
    )


@audio_router.get("/")
async def get_audio(
    id: uuid.UUID,
    user: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Получаем аудио-файл
    """

    # проверка существует ли аудио привязанное к данному юзеру
    audio = await get_audio_file_by_id_and_user_id(
        audio_id=id,
        user_id=user,
        session=session
    )
    if audio is None:
        raise HTTPException(
            status_code=404,
            detail="Файл с данными параметрами не найден."
        )

    # предоставление аудио
    file_path = f"{UPLOAD_FILES_PATH}/{user}/{audio.filename}"

    # проверяем существует ли возвращаемый файл
    try:
        os.stat(file_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден на сервере."
        )

    return FileResponse(path=file_path)
