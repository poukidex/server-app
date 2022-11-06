from http import HTTPStatus

from config.authentication import JWTCoder
from config.tests.base_test import BaseTest
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from userauth.models import Token


class TestAuth(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def _do_test_signin(
        self,
        username: str,
        pwd: str,
        expected_status: int,
        expected_user: AbstractUser = None,
    ):
        data = {"username": username, "password": pwd}
        kwargs = {}
        response = self.client.post(
            reverse("api:sign-in", kwargs=kwargs),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            self.assertIsNotNone(content["access_token"])

            self.assertIsNotNone(content["id_token"])
            self.assertTrue(
                Token.objects.filter(
                    user=expected_user, key=content["id_token"]
                ).exists()
            )

    def test_signin_user_one(self):
        self._do_test_signin(
            self.user_one.username, self.user_one_pwd, HTTPStatus.OK, self.user_one
        )

    def test_signin_user_two(self):
        self._do_test_signin(
            self.user_two.username, self.user_two_pwd, HTTPStatus.OK, self.user_two
        )

    def test_signin_user_unknown(self):
        self._do_test_signin("unknown", self.user_one_pwd, HTTPStatus.UNAUTHORIZED)

    def test_signin_bad_password(self):
        self._do_test_signin(
            self.user_one.username, "bad_password", HTTPStatus.UNAUTHORIZED
        )

    def test_refresh_access_token(self):
        self._do_test_signin(
            self.user_one.username, self.user_one_pwd, HTTPStatus.OK, self.user_one
        )
        kwargs = {}
        response = self.client.post(
            reverse("api:refresh-access-token", kwargs=kwargs),
            **self._generate_auth_user_by_token(self.token_one)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        self.assertIsNotNone(content["access_token"])

        token = Token.objects.get(user=self.user_one)
        self.assertEqual(self.token_one.key, token.key)

        self.assertEqual(JWTCoder.decode(content["access_token"]), token.key)

    def test_signout(self):
        self._do_test_signin(
            self.user_one.username, self.user_one_pwd, HTTPStatus.OK, self.user_one
        )
        kwargs = {}
        response = self.client.post(
            reverse("api:sign-out", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(Token.objects.filter(user=self.user_one).exists())
