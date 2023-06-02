from http import HTTPStatus

from django.urls import reverse

from collection.api.items import ItemViewSet
from core.models.collections import Item
from core.schemas.collections import SnapOutput
from core.tests.base import BaseTest
from viewsets.tests.abstract import Credentials, ModelViewSetTest, Payloads
from viewsets.tests.create import CreateModelViewTest
from viewsets.tests.delete import DeleteModelViewTest
from viewsets.tests.list import ListModelViewTest
from viewsets.tests.retrieve import RetrieveModelViewTest
from viewsets.tests.update import UpdateModelViewTest


class ItemViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = ItemViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.item = Item.objects.get(collection=cls.collection_1, name="item-1")

    def get_instance(self):
        return self.item

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

    retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    update = UpdateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )
    delete = DeleteModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )

    snap_payloads = Payloads(
        ok={"comment": "comment", "object_name": "object_name"},
        bad_request={"comment": "comment"},
    )

    list_snaps = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    create_snap = CreateModelViewTest(
        payloads=snap_payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
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