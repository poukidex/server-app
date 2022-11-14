from http import HTTPStatus

from ninja import Router
from userauth.models import User
from userauth.schemas import UserSchema

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
