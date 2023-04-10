from http import HTTPStatus

from django.urls import reverse
from push_notifications.models import GCMDevice

from config.tests.base_test import BaseTest


class TestDevices(BaseTest):
    def test_create_device(self):
        data = {"token": "TOKEN_FCM"}
        kwargs = {}
        response = self.client.post(
            reverse("api:devices", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        device = GCMDevice.objects.get(user=self.user_one)
        self.assertEqual(device.registration_id, "TOKEN_FCM")
