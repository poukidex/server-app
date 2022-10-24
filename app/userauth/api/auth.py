import logging
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
from config.exceptions import UnauthorizedException
from config.settings import JWT_EXPIRES_IN, JWT_KEY
from ninja import Router
from userauth.models import User
from userauth.schemas import TokenSchema
from django.contrib.auth import authenticate

router = Router()

@router.post(
    "/login",
    response={HTTPStatus.OK: TokenSchema},
    url_name="login",
    auth=None,
    operation_id="sign_in"
)
def login(request, username: str, password: str):
    user: User = authenticate(username=username, password=password)
    if not user:
        raise UnauthorizedException()

    jwt_token = generate_jwt(user)
    return HTTPStatus.OK, TokenSchema(jwt=jwt_token)


def generate_jwt(user: User):
    try:
        delta = float(JWT_EXPIRES_IN)
        expires_in = datetime.now(tz=timezone.utc) + timedelta(seconds=delta)
        return jwt.encode(
            {"user_id": str(user.id), "exp": expires_in},
            JWT_KEY,
            algorithm="HS256",
        )
    except jwt.PyJWTError:  # pragma: no cover
        raise UnauthorizedException()
