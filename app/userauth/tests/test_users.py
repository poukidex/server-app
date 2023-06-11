from __future__ import annotations

from http import HTTPStatus
from typing import Union

from django.test import TestCase
from django.urls import reverse
from ninja_crud.tests import Credentials, ListModelViewTest, ModelViewSetTest

from core.tests.base import BaseTest
from userauth.api.users import UserViewSet
from userauth.models import User
from userauth.schemas import UserOutput


class UserViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = UserViewSet

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def get_instance(self: Union[UserViewSetTest, TestCase]):
        return self.user_one

    def get_credentials_ok(self: Union[UserViewSetTest, TestCase]):
        return Credentials(ok=self.auth_user_one)

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )

    def test_get_my_user(self):
        response = self.client.get(reverse("api:my_user"), **self.auth_user_one)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        user = User.objects.get(id=content["id"])
        self.assertDictEqualsSchema(
            content,
            UserOutput.from_orm(user),
        )

    def test_update_my_user(self):
        data = {
            "object_name": "object_name",
            "username": "adupont",
            "first_name": "antoine",
            "last_name": "dupont",
        }
        response = self.client.put(
            reverse("api:my_user"),
            data=data,
            content_type="application/json",
            **self.auth_user_one,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        user = User.objects.get(id=content["id"])
        self.assertDictEqualsSchema(
            content,
            UserOutput.from_orm(user),
        )
