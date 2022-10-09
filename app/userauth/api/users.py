from http import HTTPStatus

from config import settings
from config.exceptions import UnauthorizedException
from ninja import Router
from userauth.models import User
from userauth.schemas import UserInput, UserSchema

router = Router()


@router.get(path="", response={HTTPStatus.OK: list[UserSchema]})
def list_users(request):
    return HTTPStatus.OK, User.objects.filter(is_superuser=False).all()


@router.post(path="", response={HTTPStatus.CREATED: UserSchema}, auth=None)
def create_index(request, payload: UserInput):
    if (
        payload.creation_token_password is None
        or payload.creation_token_password == ""
        or payload.creation_token_password != settings.CREATION_TOKEN_PASSWORD
    ):
        raise UnauthorizedException()

    user = User.objects.create_user(
        payload.username, payload.password, email=payload.email
    )

    return HTTPStatus.CREATED, user
