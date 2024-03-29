from http import HTTPStatus

from ninja import Router
from ninja_crud.views import ListModelView, ModelViewSet

from userauth.models import User
from userauth.schemas import UserInput, UserOutput

router = Router()


class UserViewSet(ModelViewSet):
    model = User
    output_schema = UserOutput

    list = ListModelView(output_schema=output_schema)


UserViewSet.register_routes(router)


@router.get(
    path="/me",
    url_name="my_user",
    response={HTTPStatus.OK: UserOutput},
    operation_id="retrieve_my_user",
)
def retrieve_my_user(request):
    return request.user


@router.put(
    path="/me",
    url_name="my_user",
    response={HTTPStatus.OK: UserOutput},
    operation_id="update_my_user",
)
def update_my_user(request, payload: UserInput):
    user = request.user
    for attr, value in payload.dict().items():
        setattr(user, attr, value)

    user.full_clean()
    user.save()
    return HTTPStatus.OK, user
