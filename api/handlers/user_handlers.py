from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.users import create_new_user
from api.schemas import GetToken, UserCreate
from db.session import get_db
from security import create_access_token


user_router = APIRouter()


@user_router.post("/", response_model=GetToken, status_code=201)
async def create_user(
    body: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Создание юзера
    """

    user = await create_new_user(body=body, session=session)
    # так как токен получаем только при регистрации,
    # сделаем его без срока действия (бесконечным)
    access_token = create_access_token(
        data={"sub": str(user.id)},
    )
    return GetToken(
        user_id=user.id,
        token=access_token
    )
