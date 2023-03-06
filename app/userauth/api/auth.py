from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from config.authentication import IDTokenBearer, JWTCoder
from config.exceptions import IncoherentInput
from django.contrib.auth import authenticate
from ninja import Router
from userauth.models import Token, User
from userauth.schemas import (
    AccessTokenOutput,
    PasswordResetInput,
    PasswordResetConfirmationInput,
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
    user: User = authenticate(**payload.dict())
    if not user:
        raise IncoherentInput(detail={'password': 'Username or password incorrect.'})

    token, _ = Token.objects.get_or_create(user=user)
    return HTTPStatus.OK, IDTokenOutput(id_token=token.key)


@router.post(
    "/sign-up",
    auth=None,
    response={HTTPStatus.CREATED: IDTokenOutput},
    url_name="sign-up",
    operation_id="sign_up",
)
def sign_up(request, payload: SignUpInput):
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


@router.post(
    "/reset-password",
    auth=None,
    response={HTTPStatus.NO_CONTENT: None},
    url_name="reset-password",
    operation_id="reset_password",
)
def reset_password(request, payload: PasswordResetInput):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise IncoherentInput(detail={'email': 'User with this email does not exist.'})

    # Generate a one-time use token for the user's password reset request
    token_generator = default_token_generator
    uid = urlsafe_base64_encode(force_bytes(user.id))
    token = token_generator.make_token(user)

    # Generate the password reset link URL
    password_reset_link_url = f'poukidex://password-reset/{uid}/{token}'

    # Send the password reset email to the user
    email_subject = 'Reset your password'
    email_message = render_to_string('password_reset_email.html', {
        'user': user,
        'password_reset_link_url': password_reset_link_url
    })
    plain_message = strip_tags(email_message)
    send_mail(
        subject=email_subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payload.email],
        html_message=email_message
    )
    return HTTPStatus.NO_CONTENT, None


@router.post(
    "/reset-password/confirm/{user_id}/{token}",
    auth=None,
    response={HTTPStatus.NO_CONTENT: None},
    url_name="confirm-reset-password",
    operation_id="confirm-reset-password",
)
def confirm_reset_password(request, user_id: str, token: str, payload: PasswordResetConfirmationInput):
    try:
        user_id = force_str(urlsafe_base64_decode(user_id))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(payload.password)
        user.save()
        return HTTPStatus.NO_CONTENT, None
    else:
        raise IncoherentInput(detail={'password_confirmation': 'Invalid password reset link.'})
