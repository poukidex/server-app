from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Type

from django.db.models import Model
from ninja import Router


class AbstractAPIView(ABC):
    model: Optional[Type[Model]] = None
    decorators: List[Callable] = []

    def __init__(
        self, model: Type[Model] = None, decorators: List[Callable] = None
    ) -> None:
        if decorators is None:
            decorators = []

        self.model = model
        self.decorators = decorators

    @abstractmethod
    def register_route(self, router: Router, model: Type[Model]) -> None:
        pass

    @abstractmethod
    def sub_register_route(
        self, router: Router, model: Type[Model], parent: APIViewSet
    ) -> None:
        pass


class APIViewSet:
    router: Router
    model: Type[Model]
    subsets: List[APIViewSet] = None

    def __init__(self, model: Type[Model], *args, **kwargs):
        self.model = model
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def register_routes(cls) -> None:
        cls.router = Router()
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if attr_value is not None and isinstance(attr_value, AbstractAPIView):
                attr_value.register_route(cls.router, cls.model)

        if cls.subsets is not None and isinstance(cls.subsets, list):
            for subset in cls.subsets:
                subset.register_subset_routes(cls.router)

    def register_subset_routes(self, router: Router) -> None:
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if attr_value is not None and isinstance(attr_value, AbstractAPIView):
                attr_value.sub_register_route(router, self.model, self)
