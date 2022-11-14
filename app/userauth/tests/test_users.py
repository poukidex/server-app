from http import HTTPStatus

from config.tests.base_test import BaseTest
from django.urls import reverse
from userauth.models import User
from userauth.schemas import UserSchema


class TestUsers(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_list_users(self):
        kwargs = {}
        response = self.client.get(
            reverse("api:users", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                UserSchema.from_orm(
                    User.objects.get(id=item["id"], is_superuser=False)
                ),
            )

    def test_get_my_user(self):
        response = self.client.get(reverse("api:my_user"), **self.auth_user_one)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertEqual(content["id"], str(self.user_one.id))
        self.assertDictEqualsSchema(
            content,
            UserSchema.from_orm(User.objects.get(id=content["id"], is_superuser=False)),
        )
