from typing import Any, List, Optional

from django.db.models import QuerySet
from ninja import Field, Schema
from ninja.pagination import PaginationBase

MAX_PAGINATION = 10000


class OverpoweredPagination(PaginationBase):
    class Input(Schema):
        limit: Optional[int] = Field(
            default=MAX_PAGINATION,
            description="Number of objects to retrieve by page",
            le=MAX_PAGINATION,
            ge=0,
        )
        offset: Optional[int] = Field(
            default=0, description="Offset of page to use", ge=0
        )
        order_by: Optional[List[str]]

    class Output(Schema):
        items: list[Any]
        count: int

    def paginate_queryset(self, queryset: QuerySet, pagination: Input, **params):

        # Sortering
        order_by = pagination.order_by
        if order_by is not None:
            queryset = queryset.order_by(*order_by)

        # Countering
        count = self._items_count(queryset)

        # Paginatering
        queryset = queryset[pagination.offset : pagination.offset + pagination.limit]

        return {"items": queryset, "count": count}
