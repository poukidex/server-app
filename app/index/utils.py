import logging

from config.exceptions import ConflictException, IncoherentInput
from django.core.exceptions import ValidationError
from django.db import models
from ninja import Schema


def check_object(new_object: models.Model):
    try:
        new_object.clean_fields()
    except ValidationError:
        logging.exception(f"Integrity error for object {new_object}")
        raise IncoherentInput()

    try:
        new_object.validate_unique()
    except ValidationError:
        logging.exception(f"Validation error for object {new_object}")
        raise ConflictException()


def update_object_from_schema(updated_object: models.Model, payload: Schema):
    for attr, value in payload.dict().items():
        setattr(updated_object, attr, value)

    check_object(updated_object)

    updated_object.save()