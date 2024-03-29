from __future__ import annotations

from typing import Union

from django.test import TestCase
from ninja_crud.tests import (
    CreateModelViewTest,
    Credentials,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)

from collection.api.collections import CollectionViewSet
from core.tests.base import BaseTest


class CollectionViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = CollectionViewSet

    def get_instance(self: Union[CollectionViewSetTest, TestCase]):
        return self.collection_1

    def get_credentials_ok(self: Union[CollectionViewSetTest, TestCase]):
        return Credentials(ok=self.auth_user_one, unauthorized={})

    def get_credentials_ok_forbidden(self: Union[CollectionViewSetTest, TestCase]):
        return Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two, unauthorized={}
        )

    collection_payloads = Payloads(
        ok={"name": "name", "description": "description"},
        bad_request={"name": "name"},
        conflict={"name": "collection-2", "description": "description"},
    )

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_create = CreateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_update = UpdateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials_ok_forbidden
    )

    item_payloads = Payloads(
        ok={
            "name": "new-item",
            "description": "description",
            "object_name": "object_name",
        },
        bad_request={"name": "new-item"},
        conflict={
            "name": "item-2",
            "description": "description",
            "object_name": "object_name",
        },
    )

    test_list_items = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_create_item = CreateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
