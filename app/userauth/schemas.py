from typing import Optional

from ninja import Schema
from pydantic import validator

from core.schemas import (
    IdentifiableOutput,
    OptionalStorableInput,
    OptionalStorableOutput,
)


class PasswordConfirmation(Schema):
    password: str
    password_confirmation: str

    @validator("password_confirmation")
    def passwords_match(cls, value, values, **kwargs):
        if "password" in values and value != values["password"]:
            raise ValueError("Confirmation password does not match.")
        return value


class UserUpdate(OptionalStorableInput):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]


class UserSchema(IdentifiableOutput, OptionalStorableOutput):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    fullname: str


class SignInInput(Schema):
    username: str
    password: str


class SignUpInput(Schema):
    username: str
    email: str
    password: str
    password_confirmation: str

    @validator("password_confirmation")
    def passwords_match(cls, value, values, **kwargs):
        if "password" in values and value != values["password"]:
            raise ValueError("Confirmation password does not match.")
        return value


class IDTokenOutput(Schema):
    id_token: str


class AccessTokenOutput(Schema):
    access_token: str


class PasswordResetInput(Schema):
    email: str


class PasswordResetConfirmationInput(PasswordConfirmation):
    pass


class DeviceInput(Schema):
    token: str


class DeviceOutput(Schema):
    registration_id: str
