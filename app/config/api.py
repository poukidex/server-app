import logging
from http import HTTPStatus

from django.core.exceptions import FieldError, ObjectDoesNotExist
from index.api.home import router as home_router
from ninja import NinjaAPI
from ninja.errors import ValidationError

from config.authentication import AccessTokenBearer
from config.exceptions import IndexException
from config.renderer import ORJSONRenderer
from index.api.indexes import router as index_router
from index.api.propositions import router as proposition_router
from index.api.publications import router as publication_router
from userauth.api.auth import router as auth_router
from userauth.api.users import router as users_router

api = NinjaAPI(auth=AccessTokenBearer(), urls_namespace="api", renderer=ORJSONRenderer())

api.add_router("home", home_router, tags=["home"])
api.add_router("indexes", index_router, tags=["index"])
api.add_router("publications", publication_router, tags=["publication"])
api.add_router("propositions", proposition_router, tags=["proposition"])
api.add_router("auth", auth_router, tags=["auth"])
api.add_router("users", users_router, tags=["user"])


@api.exception_handler(ValidationError)
def api_handler_validation_error(request, exc: ValidationError):
    mapped_msg = {error['loc'][-1]: error['msg'] for error in exc.errors}
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": mapped_msg},
        status=HTTPStatus.BAD_REQUEST,
    )


@api.exception_handler(IndexException)
def api_handler_index_exception(request, exc: IndexException):
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
