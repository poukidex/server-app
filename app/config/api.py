import logging
from http import HTTPStatus

from django.core.exceptions import FieldError, ObjectDoesNotExist
from ninja import NinjaAPI
from ninja.errors import ValidationError

from config.authentication import AccessTokenBearer
from config.exceptions import PoukidexException
from config.renderer import ORJSONRenderer
from poukidex.api.collections import router as collections_router
from poukidex.api.home import router as home_router
from poukidex.api.items import router as items_router
from poukidex.api.pending_items import router as pending_items_router
from poukidex.api.snaps import router as snaps_router
from userauth.api.auth import router as auth_router
from userauth.api.devices import router as devices_router
from userauth.api.users import router as users_router

api = NinjaAPI(
    auth=AccessTokenBearer(),
    urls_namespace="api",
    renderer=ORJSONRenderer(),
    servers=[],
)

api.add_router("home", home_router, tags=["home"])
api.add_router("collections", collections_router, tags=["collection"])
api.add_router("items", items_router, tags=["item"])
api.add_router("pending-items", pending_items_router, tags=["item"])
api.add_router("snaps", snaps_router, tags=["snap"])
api.add_router("auth", auth_router, tags=["auth"])
api.add_router("users", users_router, tags=["user"])
api.add_router("devices", devices_router, tags=["devices"])


@api.exception_handler(ValidationError)
def api_handler_validation_error(request, exc: ValidationError):
    mapped_msg = {error["loc"][-1]: error["msg"] for error in exc.errors}
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": mapped_msg},
        status=HTTPStatus.BAD_REQUEST,
    )


@api.exception_handler(PoukidexException)
def api_handler_poukidex_exception(request, exc: PoukidexException):
    if exc.status in [HTTPStatus.INTERNAL_SERVER_ERROR]:
        logging.exception("INTERNAL SERVER ERROR")
    return api.create_response(
        request,
        data={"message": exc.message, "detail": exc.detail},
        status=exc.status,
    )


@api.exception_handler(ObjectDoesNotExist)
def api_handle_object_not_found(request, exc):
    return api.create_response(
        request,
        {"message": "Object not found", "detail": str(exc)},
        status=HTTPStatus.NOT_FOUND,
    )


@api.exception_handler(FieldError)
def api_handle_field_error(request, exc: FieldError):
    logging.error(exc.args)
    return api.create_response(
        request,
        {
            "message": "Bad request",
            "detail": "Some fields in your request cannot be used.",
        },
        status=HTTPStatus.BAD_REQUEST,
    )


@api.exception_handler(Exception)
def api_handle_exception(request, exc):
    logging.error(f"internal error on {request.path}", exc_info=exc)
    return api.create_response(
        request,
        {"message": "Something went wrong"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
