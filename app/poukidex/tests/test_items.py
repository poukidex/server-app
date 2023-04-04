import uuid
from http import HTTPStatus

from django.db.models import Count
from django.urls import reverse

from config.tests.base_test import BaseTest
from poukidex.models import Item, Snap
from poukidex.schemas import ItemSchema, SnapSchema


class TestItems(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_retrieve_item(self):
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.get(
            reverse("api:item", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        pub = Item.objects.annotate(nb_snaps=Count("snaps")).get(
            id=self.second_collection_item_2.id
        )
        self.assertDictEqualsSchema(content, ItemSchema.from_orm(pub))

    def _do_test_update_item(self, auth_user, expected_status):
        data = {
            "name": "new-name",
            "description": "description",
            "object_name": "some_object_name",
        }
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.put(
            reverse("api:item", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            item_updated = Item.objects.get(id=self.second_collection_item_2.id)

            self.assertDictEqualsSchema(content, ItemSchema.from_orm(item_updated))

    def test_update_item(self):
        self._do_test_update_item(self.auth_user_one, HTTPStatus.OK)

    def test_update_item_forbidden(self):
        self._do_test_update_item(self.auth_user_two, HTTPStatus.FORBIDDEN)

    def test_delete_item(self):
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.delete(
            reverse("api:item", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Item.objects.filter(id=self.second_collection_item_2.id).exists()
        )

    def test_delete_item_forbidden(self):
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.delete(
            reverse("api:item", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_create_snap_unknown_item(self):
        data = {
            "comment": "some comment of this snap",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": uuid.uuid4()}
        response = self.client.post(
            reverse("api:item_snaps", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_snap(self):
        data = {
            "comment": "some comment of this snap",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.second_collection_item_1.id}
        response = self.client.post(
            reverse("api:item_snaps", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            SnapSchema.from_orm(Snap.objects.get(id=content["id"])),
        )

    def test_create_snap_conflict(self):
        data = {
            "comment": "some comment of this snap",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.post(
            reverse("api:item_snaps", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)

    def test_list_snaps(self):
        kwargs = {"id": self.second_collection_item_2.id}
        response = self.client.get(
            reverse("api:item_snaps", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                SnapSchema.from_orm(Snap.objects.get(id=item["id"])),
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
            SnapSchema.from_orm(self.second_collection_item_2_snap_1),
        )
