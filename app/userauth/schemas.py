from ninja import Schema


class UserInput(Schema):
    username: str
    password: str
    email: str


class UserSchema(Schema):
    username: str
