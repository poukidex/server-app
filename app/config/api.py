import logging
from http import HTTPStatus

from config.authentication import JWTBearer
from config.exceptions import IndexException
from ninja import NinjaAPI
from userauth.api.auth import router as auth_router
from userauth.api.users import router as users_router

from index.api.indexes import router as index_router
from index.api.propositions import router as proposition_router
from index.api.publications import router as publication_router

api = NinjaAPI(auth=JWTBearer(), urls_namespace="api")

api.add_router("indexes", index_router, tags=["index"])
api.add_router("publications", publication_router, tags=["publication"])
api.add_router("propositions", proposition_router, tags=["proposition"])
api.add_router("auth", auth_router, tags=["auth"])
api.add_router("users", users_router, tags=["user"])


@api.exception_handler(IndexException)
def api_handler_index_exception(request, exc: IndexException):
    if exc.status in [HTTPStatus.INTERNAL_SERVER_ERROR]:
        logging.exception("Error")
    return api.create_response(
        request,
        data={
            "message": exc.message,
            "status_code": exc.status,
        },
        status=exc.status,
    )
