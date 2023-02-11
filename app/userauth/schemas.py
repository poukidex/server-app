from typing import Optional
from uuid import UUID

from ninja import Schema
from pydantic import validator


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

    @validator('password_confirmation')
    def passwords_match(cls, value, values, **kwargs):
        if 'password' in values and value != values['password']:
            raise ValueError('Confirmation password does not match.')
        return value


class IDTokenOutput(Schema):
    id_token: str


class AccessTokenOutput(Schema):
    access_token: str
