from config.exceptions import ConflictException, IncoherentInput
from django.core.exceptions import ValidationError
from django.db import models
from ninja import Schema


def check_object(new_object: models.Model):
    try:
        new_object.clean_fields()
    except ValidationError:
        raise IncoherentInput()

    try:
        new_object.clean()
    except ValidationError:
        raise IncoherentInput()

    try:
        new_object.validate_unique()
    except ValidationError as error:
        raise ConflictException(detail=error.messages)

    try:
        new_object.validate_constraints()
    except ValidationError as error:
        raise ConflictException(detail=error.messages)


def update_object_from_schema(updated_object: models.Model, payload: Schema):
    for attr, value in payload.dict().items():
        setattr(updated_object, attr, value)

    check_object(updated_object)

    updated_object.save()
