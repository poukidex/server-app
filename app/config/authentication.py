import logging
from abc import ABC
from datetime import timezone, timedelta, datetime

import jwt
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer
from userauth.models import User, Token

logger = logging.getLogger(__name__)


class AbstractTokenBearer(HttpBearer, ABC):
    @staticmethod
    def _authenticate(request: HttpRequest, id_token: str) -> bool:
        if Token.objects.filter(key=id_token).exists():
            request.user = User.objects.get(auth_token__key=id_token)
            return True
        else:
            return False


class AccessTokenBearer(AbstractTokenBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        id_token = JWTCoder.decode(access_token=token)
        return self._authenticate(request, id_token=id_token)


class IDTokenBearer(AbstractTokenBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        return self._authenticate(request, id_token=token)


class JWTCoder:
    @classmethod
    def encode(cls, id_token: str) -> str | None:
        delta = float(settings.JWT_EXPIRES_IN)
        expires_in = datetime.now(tz=timezone.utc) + timedelta(seconds=delta)
        try:
            return jwt.encode(
                {"id_token": id_token, "exp": expires_in},
                settings.JWT_KEY,
                algorithm="HS256",
            )
        except jwt.PyJWTError:
            logger.exception("JWT error")

    @classmethod
    def decode(cls, access_token: str) -> str | None:
        try:
            payload = jwt.decode(jwt=access_token, key=settings.JWT_KEY, algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError:
            logger.info("JWT expired")
        except jwt.exceptions.DecodeError:
            logger.exception("JWT decode error")
        except jwt.PyJWTError:
            logger.exception("JWT error")
        else:
            return payload.get("id_token", None)
