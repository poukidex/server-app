from django.db import models
from ninja import Schema


def update_object_from_schema(updated_object: models.Model, payload: Schema):
    for attr, value in payload.dict().items():
        setattr(updated_object, attr, value)

    updated_object.full_clean()
    updated_object.save()
