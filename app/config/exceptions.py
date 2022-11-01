from http import HTTPStatus
from typing import Any


class IndexException(Exception):
    def __init__(self, status: int, message: str, detail: list = None):
        self.status = status
        self.message = message
        self.detail = detail if detail else []


class IncoherentInput(IndexException):
    def __init__(self, custom_message: str = "") -> None:
        super().__init__(
            message=f"Incoherent payload: {custom_message}",
            status=HTTPStatus.BAD_REQUEST,
        )


class ConflictException(IndexException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="This object already exists.", status=HTTPStatus.CONFLICT, *args, **kwargs
        )


class ForbiddenException(IndexException):
    def __init__(self) -> None:
        super().__init__(message="Forbidden", status=HTTPStatus.FORBIDDEN)


class UnauthorizedException(IndexException):
    def __init__(self) -> None:
        super().__init__(message="Unauthorized", status=HTTPStatus.UNAUTHORIZED)
