from __future__ import annotations

from http import HTTPStatus
from typing import Union

from django.test import TestCase
from django.urls import reverse
from ninja_crud.tests import (
    Credentials,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)

from collection.api.snaps import SnapViewSet
from core.models.collections import Item, Like, Snap
from core.tests.base import BaseTest


class SnapViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = SnapViewSet
    snap: Snap

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
        Like.objects.create(
            snap=cls.snap,
            user=cls.user_one,
            liked=True,
        )

    def get_instance(self: Union[SnapViewSetTest, TestCase]):
        return self.snap

    def get_credentials_ok(self: Union[SnapViewSetTest, TestCase]):
        return Credentials(ok=self.auth_user_one, unauthorized={})

    def get_credentials_ok_forbidden(self: Union[SnapViewSetTest, TestCase]):
        return Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two, unauthorized={}
        )

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

    def test_retrieve_my_like_ok(self):
        kwargs = {"id": self.snap.id}
        response = self.client.get(
            reverse("api:snap_like", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        like = Like.objects.get(snap_id=self.snap.id, user=self.user_one)
        self.assertEqual(content["liked"], like.liked)
        self.assertEqual(content["user"]["id"], str(like.user.id))

    def test_update_my_like_ok(self):
        kwargs = {"id": self.snap.id}
        data = {"liked": False}
        response = self.client.put(
            reverse("api:snap_like", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        like = Like.objects.get(snap_id=self.snap.id, user=self.user_one)
        self.assertEqual(content["liked"], like.liked)
        self.assertEqual(content["user"]["id"], str(like.user.id))

    def test_create_my_like_ok(self):
        kwargs = {"id": self.snap.id}
        data = {"liked": False}
        response = self.client.put(
            reverse("api:snap_like", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        like = Like.objects.get(snap_id=self.snap.id, user=self.user_two)
        self.assertEqual(content["liked"], like.liked)
        self.assertEqual(content["user"]["id"], str(like.user.id))

    def test_delete_my_like_ok(self):
        kwargs = {"id": self.snap.id}
        response = self.client.delete(
            reverse("api:snap_like", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
