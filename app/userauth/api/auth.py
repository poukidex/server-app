import logging
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
from config.exceptions import UnauthorizedException
from config.settings import JWT_EXPIRES_IN, JWT_KEY
from ninja import Router
from userauth.models import User
from userauth.schemas import ConnectionInfos, TokenSchema

router = Router()


@router.post(
    "/login",
    response={200: TokenSchema},
    url_name="login",
    auth=None,
)
def login(request, infos: ConnectionInfos):
    try:
        user: User = User.objects.get(username=infos.username)
    except Exception:
        logging.error(f"Tried to log in {infos.username} but not found")
        raise UnauthorizedException()

    if not user.check_password(infos.password):
        logging.error(f"Tried to log in {infos.username} but password not matching")
        raise UnauthorizedException()

    if JWT_KEY is None:  # pragma: no cover
        logging.critical("JWT KEY is None.")
        raise UnauthorizedException()

    try:
        delta = float(JWT_EXPIRES_IN)
        expires_in = datetime.now(tz=timezone.utc) + timedelta(seconds=delta)
        token = jwt.encode(
            {"user_id": str(user.id), "exp": expires_in},
            JWT_KEY,
            algorithm="HS256",
        )
    except jwt.PyJWTError:  # pragma: no cover
        raise UnauthorizedException()

    return HTTPStatus.OK, TokenSchema(jwt=token)
