import logging
from http import HTTPStatus

from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError

from collection.api.collections import router as collection_router
from config.authentication import AccessTokenBearer
from config.renderer import ORJSONRenderer
from core.exceptions import PoukidexException
from userauth.api.auth import router as auth_router

api = NinjaAPI(
    auth=AccessTokenBearer(),
    urls_namespace="api",
    renderer=ORJSONRenderer(),
    servers=[],
)

# api.add_router("home", home_router, tags=["home"])
api.add_router("collections", collection_router, tags=["collection"])
# api.add_router("items", ItemsAPI().router, tags=["item"])
# api.add_router("pending-items", pending_items_router, tags=["item"])
# api.add_router("snaps", snaps_router, tags=["snap"])
api.add_router("auth", auth_router, tags=["auth"])
# api.add_router("users", users_router, tags=["user"])


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


@api.exception_handler(PermissionDenied)
def api_handle_permission_denied(request, exc: PermissionDenied):
    return api.create_response(
        request,
        {
            "message": "PermissionDenied",
            "detail": "You don't have the permission to access this resource.",
        },
        status=HTTPStatus.FORBIDDEN,
    )


@api.exception_handler(NinjaValidationError)
def api_handler_ninja_validation_error(request, exc: NinjaValidationError):
    mapped_msg = {error["loc"][-1]: error["msg"] for error in exc.errors}
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": mapped_msg},
        status=HTTPStatus.BAD_REQUEST,
    )


@api.exception_handler(ValidationError)
def api_handler_validation_error(request, exc: ValidationError):
    status = HTTPStatus.BAD_REQUEST
    for field, errors in exc.error_dict.items():
        for error in errors:
            if error.code == "unique":
                status = HTTPStatus.CONFLICT
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": exc.message_dict},
        status=status,
    )
