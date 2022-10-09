from uuid import UUID

from ninja import Schema


class UserInput(Schema):
    username: str
    password: str
    email: str
    creation_token_password: str


class UserSchema(Schema):
    id: UUID
    username: str


class ConnectionInfos(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    jwt: str
