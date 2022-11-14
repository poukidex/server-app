from http import HTTPStatus

from config.authentication import IDTokenBearer, JWTCoder
from config.exceptions import IncoherentInput, UnauthorizedException
from django.contrib.auth import authenticate
from ninja import Router
from userauth.models import Token, User
from userauth.schemas import (
    AccessTokenOutput,
    ErrorOutput,
    IDTokenOutput,
    SignInInput,
    SignUpInput,
)

router = Router()


@router.post(
    "/sign-in",
    auth=None,
    response={HTTPStatus.OK: IDTokenOutput},
    url_name="sign-in",
    operation_id="sign_in",
)
def sign_in(request, payload: SignInInput):
    user: User = authenticate(username=payload.username, password=payload.password)
    if not user:
        raise UnauthorizedException()

    token, _ = Token.objects.get_or_create(user=user)
    return HTTPStatus.OK, IDTokenOutput(id_token=token.key)


@router.post(
    "/sign-up",
    auth=None,
    response={
        HTTPStatus.CREATED: IDTokenOutput,
        HTTPStatus.BAD_REQUEST: ErrorOutput,
        HTTPStatus.CONFLICT: ErrorOutput,
    },
    url_name="sign-up",
    operation_id="sign_up",
)
def sign_up(request, payload: SignUpInput):
    if payload.password != payload.password_confirmation:
        raise IncoherentInput()

    user = User.objects.create_user(
        username=payload.username, email=payload.email, password=payload.password
    )

    token, _ = Token.objects.get_or_create(user=user)
    return HTTPStatus.CREATED, IDTokenOutput(id_token=token.key)


@router.post(
    "/token/refresh",
    auth=IDTokenBearer(),
    response={HTTPStatus.OK: AccessTokenOutput},
    url_name="refresh-access-token",
    operation_id="refresh_access_token",
)
def refresh_access_token(request):
    id_token = request.user.auth_token.key
    access_token = JWTCoder.encode(id_token)
    if access_token is None:  # pragma: no cover
        raise IncoherentInput()
    return HTTPStatus.OK, AccessTokenOutput(access_token=access_token)


@router.post(
    "/token/rotate",
    response={HTTPStatus.OK: IDTokenOutput},
    url_name="rotate-id-token",
    operation_id="rotate_id_token",
)
def rotate_id_token(request):
    request.user.auth_token.delete()
    token = Token.objects.create(user=request.user)
    return HTTPStatus.OK, IDTokenOutput(id_token=token.key)


@router.post(
    "/sign-out",
    response={HTTPStatus.NO_CONTENT: None},
    url_name="sign-out",
    operation_id="sign_out",
)
def sign_out(request):
    request.user.auth_token.delete()
    return HTTPStatus.NO_CONTENT, None
