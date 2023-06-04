from http import HTTPStatus

from django.urls import reverse

from collection.api.snaps import SnapViewSet
from core.models.collections import Item, Like, Snap
from core.tests.base import BaseTest
from viewsets.tests.abstract import Credentials, ModelViewSetTest, Payloads
from viewsets.tests.delete import DeleteModelViewTest
from viewsets.tests.list import ListModelViewTest
from viewsets.tests.retrieve import RetrieveModelViewTest
from viewsets.tests.update import UpdateModelViewTest


class SnapViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = SnapViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        item = Item.objects.get(collection=cls.collection_1, name="item-1")
        cls.snap = Snap.objects.create(
            item=item,
            user=cls.user_one,
            comment="Random comment",
            object_name="some object_name",
        )

    def get_instance(self):
        return self.snap

    def get_credentials_ok(self):
        return Credentials(ok=self.auth_user_one)

    def get_credentials_ok_forbidden(self):
        return Credentials(ok=self.auth_user_one, forbidden=self.auth_user_two)

    snap_payloads = Payloads(
        ok={"comment": "comment", "object_name": "object_name"},
        bad_request={"comment": "comment"},
    )

    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_update = UpdateModelViewTest(
        payloads=snap_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials_ok_forbidden
    )

    test_list_likes = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )

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
