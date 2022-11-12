from typing import Optional
from uuid import UUID

from ninja import Schema


class ErrorOutput(Schema):
    status: int
    message: str
    detail: list | dict


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


class SignInOutput(Schema):
    id_token: str
    access_token: str


class RefreshAccessTokenOutput(Schema):
    access_token: str


class SignUpInput(Schema):
    username: str
    email: str
    password: str
    password_confirmation: str


class SignUpOutput(SignInOutput):
    pass
