from http import HTTPStatus

import jwt
from config import settings
from config.tests.base_test import BaseTest
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class TestAuth(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def _do_test_login(
        self,
        username: str,
        pwd: str,
        expected_status: int,
        expected_user: AbstractUser = None,
    ):
        # data = {"username": username, "password": pwd}
        kwargs = {}
        response = self.client.post(
            reverse("api:login", kwargs=kwargs)
            + f"?username={username}&password={pwd}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            self.assertIsNotNone(content["jwt"])

            payload = jwt.decode(
                jwt=content["jwt"], key=settings.JWT_KEY, algorithms=["HS256"]
            )

            user_id = payload.get("user_id")

            self.assertEqual(user_id, str(expected_user.id))

    def test_login_user_one(self):
        self._do_test_login(
            self.user_one.username, self.user_one_pwd, HTTPStatus.OK, self.user_one
        )

    def test_login_user_two(self):
        self._do_test_login(
            self.user_two.username, self.user_two_pwd, HTTPStatus.OK, self.user_two
        )

    def test_login_user_unknown(self):
        self._do_test_login("unknown", self.user_one_pwd, HTTPStatus.UNAUTHORIZED)

    def test_login_bad_password(self):
        self._do_test_login(
            self.user_one.username, "bad_password", HTTPStatus.UNAUTHORIZED
        )
