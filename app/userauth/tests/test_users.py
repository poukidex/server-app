from http import HTTPStatus

from django.urls import reverse

from core.tests.base import BaseTest
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
        self.assertEqual(len(content), 3)
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

    def test_update_profile(self):
        data = {
            "object_name": "some_object_name",
            "username": "new-username",
            "first_name": "antoine",
            "last_name": "dupont",
        }
        response = self.client.put(
            reverse("api:my_user"),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertEqual(content["id"], str(self.user_one.id))
        user = User.objects.get(id=content["id"])
        self.assertDictEqualsSchema(
            content,
            UserSchema.from_orm(user),
        )
        self.assertEqual(user.object_name, "some_object_name")
        self.assertEqual(user.username, "new-username")
        self.assertEqual(user.first_name, "antoine")
        self.assertEqual(user.last_name, "dupont")
        self.assertEqual(
            content["presigned_url"], "presigned_url"
        )  # mock return 'presigned_url'
