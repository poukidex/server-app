import logging

import jwt
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer

from .models import Deployment

logger = logging.getLogger(__name__)


class TokenBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        return token == settings.SERVING_API_KEY


class JWTBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        try:
            payload = jwt.decode(token, settings.JWT_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            return False
        except Exception:
            logger.exception("error decoding jwt")
            return False

        deployment_id = payload.get("deployment_id")
        if not deployment_id:
            return False
        if Deployment.objects.filter(pk=deployment_id).exists():
            return payload
        return False