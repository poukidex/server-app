from __future__ import annotations

from http import HTTPStatus
from typing import Union

from django.test import TestCase
from django.urls import reverse
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

from collection.api.items import ItemViewSet
from core.models.collections import Item
from core.schemas.collections import SnapOutput
from core.tests.base import BaseTest


class ItemViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = ItemViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.item = Item.objects.get(collection=cls.collection_1, name="item-1")

    def get_instance(self: Union[ItemViewSetTest, TestCase]):
        return self.item

    def get_credentials_ok(self: Union[ItemViewSetTest, TestCase]):
        return Credentials(ok=self.auth_user_one, unauthorized={})

    def get_credentials_ok_forbidden(self: Union[ItemViewSetTest, TestCase]):
        return Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two, unauthorized={}
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

    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_update = UpdateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials_ok_forbidden
    )

    snap_payloads = Payloads(
        ok={"comment": "comment", "object_name": "object_name"},
        bad_request={"comment": "comment"},
    )

    test_list_snaps = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_create_snap = CreateModelViewTest(
        payloads=snap_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )

    def test_retrieve_my_snap(self):
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.get(
            reverse("api:my_snap", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            SnapOutput.from_orm(self.second_collection_item_2_snap_1),
        )
