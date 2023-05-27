import re
from typing import Type

from ninja import Schema


def to_snake_case(name: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def schema_with_optional_fields(schema: Type[Schema]) -> Type[Schema]:
    class OptionalSchema(schema):
        ...

    for field in OptionalSchema.__fields__.values():
        field.required = False

    OptionalSchema.__name__ = f"Optional{schema.__name__}"
    return OptionalSchema


def merge_decorators(decorators):
    def merged_decorator(func):
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return merged_decorator
