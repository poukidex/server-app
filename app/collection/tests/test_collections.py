from http import HTTPStatus

from django.db.models import Count
from django.urls import reverse

from core.models.collections import Collection, Item, PendingItem
from core.schemas.collections import CollectionOutput, ItemOutput, PendingItemSchema
from core.tests.base import BaseTest


class TestCollections(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_list_collections(self):
        kwargs = {}
        response = self.client.get(
            reverse("api:collections", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                CollectionOutput.from_orm(
                    Collection.objects.annotate(nb_items=Count("items")).get(
                        id=item["id"]
                    )
                ),
            )

    def test_create_collection(self):
        data = {
            "name": "new-collection",
            "description": "some description of this collection",
        }
        kwargs = {}
        response = self.client.post(
            reverse("api:collections", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        new_collection = Collection.objects.get(name="new-collection")
        self.assertDictEqualsSchema(content, CollectionOutput.from_orm(new_collection))

    def test_retrieve_collection(self):
        kwargs = {"id": self.first_collection.id}
        response = self.client.get(
            reverse("api:collection", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content, CollectionOutput.from_orm(self.first_collection)
        )

    def test_update_collection(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.first_collection.id}
        response = self.client.put(
            reverse("api:collection", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        collection_updated = Collection.objects.get(id=self.first_collection.id)

        self.assertDictEqualsSchema(
            content, CollectionOutput.from_orm(collection_updated)
        )

    def test_update_collection_forbidden(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.first_collection.id}
        response = self.client.put(
            reverse("api:collection", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_collection(self):
        kwargs = {"id": self.first_collection.id}
        response = self.client.delete(
            reverse("api:collection", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Collection.objects.filter(id=self.first_collection.id).exists()
        )

    def test_delete_collection_forbidden(self):
        kwargs = {"id": self.first_collection.id}
        response = self.client.delete(
            reverse("api:collection", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def _do_test_create_pending_item(self, auth_user):
        data = {
            "name": "item4",
            "description": "some description of this item",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_collection.id}
        response = self.client.post(
            reverse("api:collection_pending_items", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            PendingItemSchema.from_orm(PendingItem.objects.get(id=content["id"])),
        )

    def test_create_pending_item_owner(self):
        self._do_test_create_pending_item(self.auth_user_one)

    def test_create_pending_item_user(self):
        self._do_test_create_pending_item(self.auth_user_two)

    def test_create_item(self):
        data = {
            "name": "item1",
            "description": "some description of this item",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_collection.id}
        response = self.client.post(
            reverse("api:collection_items", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            ItemOutput.from_orm(Item.objects.get(id=content["id"])),
        )

    def _do_test_list_pending_items(self, auth_user, expected_number):
        kwargs = {"id": self.second_collection.id}
        response = self.client.get(
            reverse("api:collection_pending_items", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), expected_number)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                PendingItemSchema.from_orm(PendingItem.objects.get(id=item["id"])),
            )

    def test_list_pending_items_owner(self):
        self._do_test_list_pending_items(self.auth_user_one, 1)

    def test_list_pending_items_creator(self):
        self._do_test_list_pending_items(self.auth_user_two, 1)

    def test_list_pending_items_user(self):
        self._do_test_list_pending_items(self.auth_user_three, 0)

    def test_create_item_forbidden(self):
        data = {
            "name": "item1",
            "description": "some description of this item",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_collection.id}
        response = self.client.post(
            reverse("api:collection_items", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_list_items(self):
        kwargs = {"id": self.second_collection.id}
        response = self.client.get(
            reverse("api:collection_items", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                ItemOutput.from_orm(
                    Item.objects.annotate(nb_snaps=Count("snaps")).get(id=item["id"])
                ),
            )
