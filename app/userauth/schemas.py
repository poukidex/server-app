from datetime import datetime
from typing import Optional
from uuid import UUID
from django import models
from ninja import Schema


class UserInput(Schema):
    username: str
    password: str
    email: str

class UserSchema(Schema):
    username: str
