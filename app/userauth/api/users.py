from http import HTTPStatus

from config import settings
from config.exceptions import UnauthorizedException
from ninja import Router
from userauth.models import User
from userauth.schemas import UserInput, UserSchema

router = Router()


@router.get(path="", url_name="users", response={HTTPStatus.OK: list[UserSchema]})
def list_users(request):
    return HTTPStatus.OK, User.objects.filter(is_superuser=False).all()


@router.post(
    path="", url_name="users", response={HTTPStatus.CREATED: UserSchema}
)
def create_user(request, payload: UserInput):
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


@router.get(path="/me", url_name="my_user", response={HTTPStatus.OK: UserSchema}, operation_id="get_my_user")
def get_my_user(request):
    return request.user
