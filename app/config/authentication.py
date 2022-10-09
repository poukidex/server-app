import logging

import jwt
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer
from userauth.models import User

logger = logging.getLogger(__name__)


class JWTBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        if token is None or token == "":
            return False

        try:
            payload = jwt.decode(jwt=token, key=settings.JWT_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            return False
        except Exception:
            logger.exception("error decoding jwt")
            return False

        user_id = payload.get("user_id")
        if not user_id:
            return False

        if User.objects.filter(id=user_id).exists():
            request.user = User.objects.get(id=user_id)
            return True

        return False
