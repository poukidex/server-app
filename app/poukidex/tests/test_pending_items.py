from http import HTTPStatus

from django.urls import reverse

from config.tests.base_test import BaseTest
from core.enums import PendingItemStatus
from poukidex.models import Item, PendingItem
from poukidex.schemas import ItemSchema, PendingItemSchema


class TestPendingItems(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def _do_test_update_pending_item(self, auth_user, expected_status):
        data = {
            "name": "new-name",
            "description": "description",
            "object_name": "some_object_name",
        }
        kwargs = {"id": self.second_collection_pending_item.id}
        response = self.client.put(
            reverse("api:pending_item", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            item_updated = PendingItem.objects.get(
                id=self.second_collection_pending_item.id
            )

            self.assertDictEqualsSchema(
                content, PendingItemSchema.from_orm(item_updated)
            )

    def test_update_pending_item(self):
        self._do_test_update_pending_item(self.auth_user_one, HTTPStatus.OK)

    def test_update_pending_item_creator(self):
        self._do_test_update_pending_item(self.auth_user_two, HTTPStatus.OK)

    def test_update_pending_item_forbidden(self):
        self._do_test_update_pending_item(self.auth_user_three, HTTPStatus.FORBIDDEN)

    def _do_test_delete_pending_item(self, auth_user, expected_status):
        kwargs = {"id": self.second_collection_pending_item.id}
        response = self.client.delete(
            reverse("api:pending_item", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.NO_CONTENT:
            self.assertFalse(
                PendingItem.objects.filter(
                    id=self.second_collection_pending_item.id
                ).exists()
            )

    def test_delete_pending_item(self):
        self._do_test_delete_pending_item(self.auth_user_one, HTTPStatus.NO_CONTENT)

    def test_delete_pending_item_creator(self):
        self._do_test_delete_pending_item(self.auth_user_two, HTTPStatus.NO_CONTENT)

    def test_delete_pending_item_forbidden(self):
        self._do_test_delete_pending_item(self.auth_user_three, HTTPStatus.FORBIDDEN)

    def _do_test_accept_pending_item(self, auth_user, expected_status):
        kwargs = {"id": self.second_collection_pending_item.id}
        response = self.client.put(
            reverse("api:accept_pending_item", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()
            item = Item.objects.get(name=self.second_collection_pending_item.name)
            self.assertDictEqualsSchema(content, ItemSchema.from_orm(item))

            pending_item = PendingItem.objects.get(
                id=self.second_collection_pending_item.id
            )
            self.assertEqual(pending_item.status, PendingItemStatus.ACCEPTED)

    def test_accept_pending_item(self):
        self._do_test_accept_pending_item(self.auth_user_one, HTTPStatus.CREATED)

    def test_accept_pending_item_wrong_status(self):
        self.second_collection_pending_item.status = PendingItemStatus.ACCEPTED
        self.second_collection_pending_item.save()
        self._do_test_accept_pending_item(self.auth_user_one, HTTPStatus.BAD_REQUEST)

    def test_accept_pending_item_creator(self):
        self._do_test_accept_pending_item(self.auth_user_two, HTTPStatus.FORBIDDEN)

    def _do_test_refuse_pending_item(self, auth_user, expected_status):
        kwargs = {"id": self.second_collection_pending_item.id}
        response = self.client.put(
            reverse("api:refuse_pending_item", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.NO_CONTENT:
            self.assertFalse(
                Item.objects.filter(
                    name=self.second_collection_pending_item.name
                ).exists()
            )
            pending_item = PendingItem.objects.get(
                id=self.second_collection_pending_item.id
            )
            self.assertEqual(pending_item.status, PendingItemStatus.REFUSED)

    def test_refuse_pending_item(self):
        self._do_test_refuse_pending_item(self.auth_user_one, HTTPStatus.NO_CONTENT)

    def test_refuse_pending_item_creator(self):
        self._do_test_refuse_pending_item(self.auth_user_two, HTTPStatus.FORBIDDEN)

    def test_refuse_pending_item_wrong_status(self):
        self.second_collection_pending_item.status = PendingItemStatus.ACCEPTED
        self.second_collection_pending_item.save()
        self._do_test_refuse_pending_item(self.auth_user_one, HTTPStatus.BAD_REQUEST)
