from config.exceptions import ConflictException, IncoherentInput
from django.core.exceptions import ValidationError
from django.db import models
from ninja import Schema


def check_object(new_object: models.Model):
    try:
        new_object.clean_fields()
    except ValidationError as error:
        raise IncoherentInput(detail=error.message_dict)

    try:
        new_object.validate_unique()
        new_object.validate_constraints()
    except ValidationError as error:
        raise ConflictException(detail=error.message_dict)


def update_object_from_schema(updated_object: models.Model, payload: Schema):
    for attr, value in payload.dict().items():
        setattr(updated_object, attr, value)

    check_object(updated_object)

    updated_object.save()
