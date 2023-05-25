from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.users import get_user_by_uuid
from db.models import User
from db.session import get_db
from settings import ALGORITHM, SECRET_KEY

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db),
) -> User | HTTPException:
    """
    Получаем текущего юзера по токену
    """
    exception = HTTPException(
        status_code=401,
        detail='Невалидный токен'
    )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise exception
    except JWTError:
        raise exception

    user = await get_user_by_uuid(user_id=user_id, session=session)
    if user is None:
        raise exception
    return user
