from http import HTTPStatus

from config import settings
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

    def _do_test_create_user(
        self, username: str, email: str, expected_status: int, false_token: bool = False
    ):
        data = {
            "username": username,
            "password": "cool_password",
            "email": email,
            "creation_token_password": settings.CREATION_TOKEN_PASSWORD,
        }
        if false_token:
            data["creation_token_password"] = "false_token"

        kwargs = {}
        response = self.client.post(
            reverse("api:users", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.CREATED:
            content = response.json()
            new_user = User.objects.get(username=username, id=content["id"])
            self.assertDictEqualsSchema(content, UserSchema.from_orm(new_user))

    def test_create_user(self):
        self._do_test_create_user(
            "cool_name", "cool_email@email.com", HTTPStatus.CREATED
        )

    def test_create_user_conflict(self):
        self._do_test_create_user(
            self.user_one.username, "cool_email@email.com", HTTPStatus.CONFLICT
        )

    def test_create_user_conflict_email(self):
        self._do_test_create_user("cool_name", self.user_one.email, HTTPStatus.CONFLICT)

    def test_create_user_conflict_bad_token(self):
        self._do_test_create_user(
            "cool_name",
            "cool_email@email.com",
            HTTPStatus.UNAUTHORIZED,
            false_token=True,
        )

    def test_create_user_conflict_bad_email(self):
        self._do_test_create_user(
            "cool_name", "malformatedemail", HTTPStatus.BAD_REQUEST
        )
