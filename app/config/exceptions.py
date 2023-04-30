from http import HTTPStatus
from typing import Any


class PoukidexException(Exception):
    def __init__(self, status: int, message: str, detail: list | dict = None):
        self.status = status
        self.message = message
        self.detail = detail if detail else None


class IncoherentInput(PoukidexException):
    def __init__(self, custom_message: str = "", *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message=f"Incoherent payload: {custom_message}",
            status=HTTPStatus.BAD_REQUEST,
            *args,
            **kwargs,
        )


class ConflictException(PoukidexException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="This object already exists.",
            status=HTTPStatus.CONFLICT,
            *args,
            **kwargs,
        )


class ForbiddenException(PoukidexException):
    def __init__(self) -> None:
        super().__init__(message="Forbidden", status=HTTPStatus.FORBIDDEN)


class UnauthorizedException(PoukidexException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="Unauthorized", status=HTTPStatus.UNAUTHORIZED, *args, **kwargs
        )
