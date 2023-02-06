from typing import Optional
from uuid import UUID

from ninja import Schema


class ErrorOutput(Schema):
    status: int
    message: str
    detail: dict[str, str]


class UserInput(Schema):
    username: str
    password: str
    email: str
    creation_token_password: str


class UserSchema(Schema):
    id: UUID
    username: str
    picture: Optional[str]


class SignInInput(Schema):
    username: str
    password: str


class SignUpInput(Schema):
    username: str
    email: str
    password: str
    password_confirmation: str


class IDTokenOutput(Schema):
    id_token: str


class AccessTokenOutput(Schema):
    access_token: str
