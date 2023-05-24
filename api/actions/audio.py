import os
import uuid

from pydub import AudioSegment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Audio


async def upload_audio_file(
        filename: str,
        user_id: uuid.UUID,
        owner_id: uuid.UUID,
        session: AsyncSession
) -> Audio:
    """
    Загружаем файл в БД
    """
    async with session.begin():
        audio = Audio(
            filename=filename,
            user_id=user_id,
            owner_id=owner_id,
        )
        session.add(audio)
        await session.commit()
        return audio


async def convert_from_wav_to_mp3(
        upload_path: str,
        filename: str
) -> str:
    """
    Конвертируем файл из формата wav в mp3
    """

    mp3_filename = '.'.join(filename.split('.')[:-1]) + '.mp3'
    sound = AudioSegment.from_wav(f'{upload_path}/{filename}')
    sound.export(f'{upload_path}/{mp3_filename}', format="mp3")
    os.remove(f'{upload_path}/{filename}')
    return mp3_filename


async def get_audio_file_by_id_and_user_id(
        audio_id: uuid.UUID,
        user_id: uuid.UUID,
        session: AsyncSession
) -> Audio | None:
    """
    Получаем audio по UUID
    """

    async with session.begin():
        query = select(Audio).where(Audio.id == audio_id,
                                    Audio.user_id == user_id)
        res = await session.execute(query)
        audio = res.fetchone()
        if audio is not None:
            return audio[0]
