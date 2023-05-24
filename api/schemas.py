import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, validator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")


class GetToken(BaseModel):
    user_id: uuid.UUID
    token: str


class UserCreate(BaseModel):
    username: str

    @validator("username")
    def validate_username(cls, value):
        if not USERNAME_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail="Username может содержать только латиницу и цифры",
            )
        elif len(value) < 6 or len(value) > 29:
            raise HTTPException(
                status_code=422,
                detail="Username должен быть больше 6 символов, но меньше 30"
            )
        return value


class GetAudio(BaseModel):
    link: str
