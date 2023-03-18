from http import HTTPStatus

from ninja import Router

from core.utils import update_object_from_schema
from userauth.models import User
from userauth.schemas import UserSchema, UserUpdate

router = Router()


@router.get(path="", url_name="users", response={HTTPStatus.OK: list[UserSchema]})
def list_users(request):
    return HTTPStatus.OK, User.objects.filter(is_superuser=False).all()


@router.get(
    path="/me",
    url_name="my_user",
    response={HTTPStatus.OK: UserSchema},
    operation_id="get_my_user",
)
def get_my_user(request):
    return request.user


@router.put(
    path="/me",
    url_name="my_user",
    response={HTTPStatus.OK: UserSchema},
    operation_id="update_my_user",
)
def update_my_user(request, payload: UserUpdate):
    user = request.user
    update_object_from_schema(user, payload)
    return HTTPStatus.OK, user
