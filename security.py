from jose import jwt

from settings import ALGORITHM, SECRET_KEY


def create_access_token(data: dict):
    """
    Создаем токен
    """

    encoded_jwt = jwt.encode(
        claims=data,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt
