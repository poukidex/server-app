from http import HTTPStatus

from config.authentication import IDTokenBearer, JWTCoder
from config.exceptions import IncoherentInput, UnauthorizedException
from django.contrib.auth import authenticate
from ninja import Router
from userauth.models import Token, User
from userauth.schemas import RefreshAccessTokenOutput, SignInInput, SignInOutput

router = Router()


@router.post(
    "/sign-in",
    auth=None,
    response={HTTPStatus.OK: SignInOutput},
    url_name="sign-in",
    operation_id="sign_in",
)
def sign_in(request, payload: SignInInput):
    user: User = authenticate(username=payload.username, password=payload.password)
    if not user:
        raise UnauthorizedException()

    token, _ = Token.objects.get_or_create(user=user)
    access_token = JWTCoder.encode(token.key)
    if access_token is None:  # pragma: no cover
        raise UnauthorizedException()
    return HTTPStatus.OK, SignInOutput(id_token=token.key, access_token=access_token)


@router.post(
    "/refresh-access-token",
    auth=IDTokenBearer(),
    response={HTTPStatus.OK: RefreshAccessTokenOutput},
    url_name="refresh-access-token",
    operation_id="refresh_access_token",
)
def refresh_access_token(request):
    id_token = request.user.auth_token.key
    access_token = JWTCoder.encode(id_token)
    if access_token is None:  # pragma: no cover
        raise IncoherentInput()
    return HTTPStatus.OK, RefreshAccessTokenOutput(access_token=access_token)


@router.post(
    "/sign-out",
    response={HTTPStatus.NO_CONTENT: None},
    url_name="sign-out",
    operation_id="sign_out",
)
def sign_out(request):
    Token.objects.get(user=request.user).delete()
    return HTTPStatus.NO_CONTENT, None
