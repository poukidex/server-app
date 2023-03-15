from http import HTTPStatus

from index.api.utils import generate_presigned_url_for_object
from index.schemas import ImageUploadInput, ImageUploadSchema
from ninja import Router
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


@router.post(
    path="/me/picture/upload",
    url_name="user_picture_upload",
    response={HTTPStatus.OK: ImageUploadSchema},
    operation_id="generate_user_picture_presigned_url",
)
def generate_presigned_url_for_upload(request, payload: ImageUploadInput):
    return generate_presigned_url_for_object(
        request.user, payload.filename, payload.content_type
    )


@router.put(
    path="/me",
    url_name="my_user",
    response={HTTPStatus.OK: UserSchema},
    operation_id="update_my_user",
)
def update_my_user(request, payload: UserUpdate):
    user = request.user
    user.picture_object_name = payload.picture_object_name
    user.save()
    return HTTPStatus.OK, user
