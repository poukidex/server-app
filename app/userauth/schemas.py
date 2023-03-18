from typing import Optional
from uuid import UUID

from ninja import Schema
from pydantic import validator


class PasswordConfirmation(Schema):
    password: str
    password_confirmation: str

    @validator("password_confirmation")
    def passwords_match(cls, value, values, **kwargs):
        if "password" in values and value != values["password"]:
            raise ValueError("Confirmation password does not match.")
        return value


class UserUpdate(Schema):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    object_name: Optional[str]


class UserSchema(UserUpdate):
    id: UUID
    presigned_url: Optional[str]
    fullname: str


class SignInInput(Schema):
    username: str
    password: str


class SignUpInput(PasswordConfirmation):
    username: str
    email: str


class IDTokenOutput(Schema):
    id_token: str


class AccessTokenOutput(Schema):
    access_token: str


class PasswordResetInput(Schema):
    email: str


class PasswordResetConfirmationInput(PasswordConfirmation):
    pass
