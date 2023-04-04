from http import HTTPStatus

from django.urls import reverse

from config.tests.base_test import BaseTest
from poukidex.models import Item, Like, Snap
from poukidex.schemas import SnapSchema


class TestSnap(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_retrieve_snap(self):
        kwargs = {"id": self.second_collection_item_2_snap_2.id}
        response = self.client.get(
            reverse("api:snap", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            SnapSchema.from_orm(self.second_collection_item_2_snap_2),
        )

    def _do_test_update_snap(self, auth_user, expected_status):
        data = {"comment": "some comment", "object_name": "some_object_name"}
        kwargs = {"id": self.second_collection_item_2_snap_1.id}
        response = self.client.put(
            reverse("api:snap", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            snap_updated = Snap.objects.get(id=self.second_collection_item_2_snap_1.id)

            self.assertDictEqualsSchema(content, SnapSchema.from_orm(snap_updated))

    def test_update_snap(self):
        self._do_test_update_snap(self.auth_user_one, HTTPStatus.OK)

    def test_update_snap_forbidden(self):
        self._do_test_update_snap(self.auth_user_two, HTTPStatus.FORBIDDEN)

    def test_delete_snap(self):
        kwargs = {"id": self.second_collection_item_2_snap_1.id}
        response = self.client.delete(
            reverse("api:snap", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Item.objects.filter(id=self.second_collection_item_2_snap_1.id).exists()
        )

    def test_delete_snap_by_creator(self):
        kwargs = {"id": self.second_collection_item_2_snap_2.id}
        response = self.client.delete(
            reverse("api:snap", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Item.objects.filter(id=self.second_collection_item_2_snap_1.id).exists()
        )

    def test_delete_snap_forbidden(self):
        kwargs = {"id": self.second_collection_item_2_snap_1.id}
        response = self.client.delete(
            reverse("api:snap", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def _do_test_like(
        self,
        approval: bool,
        snap: Snap,
        auth_user,
        user,
        expected_code: int,
    ):
        data = {"liked": approval}
        kwargs = {"id": snap.id}
        response = self.client.post(
            reverse("api:snap_likes", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_code)

        if expected_code == HTTPStatus.OK:
            content = response.json()
            self.assertEqual(content["liked"], approval)
            self.assertEqual(content["user"]["id"], str(user.id))
            approbation = Like.objects.get(snap=snap, user=user)
            self.assertEqual(approbation.liked, approval)

    def test_like(self):
        self._do_test_like(
            True,
            self.second_collection_item_2_snap_2,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.OK,
        )

    def test_dislike(self):
        self._do_test_like(
            False,
            self.second_collection_item_2_snap_2,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.OK,
        )

    def test_like_my_snap(self):
        self._do_test_like(
            True,
            self.second_collection_item_2_snap_1,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.OK,
        )

    def test_get_my_approbation(self):
        Like.objects.create(
            snap=self.second_collection_item_2_snap_2,
            user=self.user_one,
            liked=True,
        )

        kwargs = {"id": self.second_collection_item_2_snap_2.id}
        response = self.client.get(
            reverse("api:snap_like", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        self.assertEqual(content["liked"], True)
        self.assertEqual(content["user"]["id"], str(self.user_one.id))

    def test_list_approbations(self):
        app1 = Like.objects.create(
            snap=self.second_collection_item_2_snap_2,
            user=self.user_one,
            liked=True,
        )

        app2 = Like.objects.create(
            snap=self.second_collection_item_2_snap_2,
            user=self.user_two,
            liked=True,
        )

        kwargs = {"id": self.second_collection_item_2_snap_2.id}
        response = self.client.get(
            reverse("api:snap_likes", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        ids = [app["id"] for app in content]

        self.assertIn(app1.id, ids)
        self.assertIn(app2.id, ids)

    def test_delete_my_approbation(self):
        Like.objects.create(
            snap=self.second_collection_item_2_snap_2,
            user=self.user_one,
            liked=True,
        )

        kwargs = {"id": self.second_collection_item_2_snap_2.id}
        response = self.client.delete(
            reverse("api:snap_like", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
