from typing import Type

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import Field
from ninja import Schema

from core.exceptions import ConflictException, IncoherentInput


def check_object(
    model_object: models.Model,
    exclude=None,
    validate_unique=True,
    validate_constraints=True,
):
    """
    Attempts to mimic the django Model.full_clean() by calling
    clean_fields(), clean(), validate_unique(), and validate_constraints() on the model.
    """

    if exclude is None:
        exclude = set()
    else:
        exclude = set(exclude)

    try:
        model_object.clean_fields(exclude=exclude)
    except ValidationError as error:
        raise IncoherentInput(detail=error.message_dict)

    try:
        model_object.clean()
    except ValidationError as error:
        raise IncoherentInput(detail=error.message_dict)

    if validate_unique:
        try:
            model_object.validate_unique(exclude=exclude)
        except ValidationError as error:
            raise ConflictException(detail=error.message_dict)

    if validate_constraints:
        try:
            model_object.validate_constraints(exclude=exclude)
        except ValidationError as error:
            raise ConflictException(detail=error.message_dict)


def update_object_from_schema(updated_object: models.Model, payload: Schema):
    for attr, value in payload.dict().items():
        setattr(updated_object, attr, value)

    check_object(updated_object)

    updated_object.save()


def update_object_from_dict(
    model_object: models.Model, dict_object: dict
) -> models.Model:
    for attr, value in dict_object.items():
        field: Field = model_object._meta.get_field(attr)

        # not field.is_relation => attribute
        if not field.is_relation:
            setattr(model_object, attr, value)

        # many_to_one => foreign key id
        elif field.many_to_one:
            setattr(model_object, attr, value)

        else:
            raise Exception(
                f"The relation type {field.get_internal_type()} has not been implemented..."
            )

    check_object(model_object)

    model_object.save()

    return model_object


def patch_object_from_schema(
    model_object: models.Model, schema_object: Schema
) -> models.Model:
    return update_object_from_dict(
        model_object, dict_object=schema_object.dict(exclude_none=True)
    )


def create_object_from_schema(
    model_class: Type[models.Model], schema_object: Schema, **kwargs
) -> models.Model:
    model_object = model_class(**kwargs)
    return update_object_from_dict(
        model_object, dict_object=schema_object.dict(exclude_unset=True)
    )


def check_and_create_multiple_objects(
    object_class, objects: list[models.Model]
) -> list:
    error_messages: list[dict | None] = [None] * len(objects)
    for index, element in enumerate(objects):
        try:
            element.clean_fields()
        except ValidationError as error:
            error_messages[index] = dict(error=error.messages)

    if any(error_messages):
        raise IncoherentInput(detail=error_messages)

    for index, element in enumerate(objects):
        try:
            element.validate_constraints()
        except ValidationError as error:
            error_messages[index] = dict(error=error.messages)

    if any(error_messages):
        raise ConflictException(detail=error_messages)

    try:
        with transaction.atomic():
            created_elements = object_class.objects.bulk_create(objects)
        return created_elements
    except IntegrityError as error:
        raise ConflictException(detail=list(error.args))
