from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from django.urls import reverse

from core.models.collections import Item, Snap
from core.schemas.collections import SnapOutput
from core.tests.base import BaseTest


class TestHome(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.item_another = Item.objects.create(
            collection=cls.collection_2,
            name="another-item",
            description="description",
            object_name="object_name",
        )

    def _do_test_list_snaps(self, since_datetime, expected_number):
        Snap.objects.all().delete()

        d1 = datetime.now(tz=timezone.utc) - timedelta(days=2)
        snap_1 = Snap.objects.create(
            item=self.item_another,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
            created_at=d1,
        )
        snap_1.created_at = d1
        snap_1.save()

        d2 = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
        snap_2 = Snap.objects.create(
            item=self.second_collection_item_2,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
        )
        snap_2.created_at = d2
        snap_2.save()

        d3 = datetime.now(tz=timezone.utc)
        snap_3 = Snap.objects.create(
            item=self.second_collection_item_1,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
            created_at=d3,
        )
        snap_3.created_at = d3
        snap_3.save()

        url = reverse("api:feed") + "?order_by=created_at"
        if since_datetime:
            since_datetime = since_datetime.timestamp()
            url += f"&since={since_datetime}"

        response = self.client.get(url, **self.auth_user_one)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), expected_number)
        ids = []
        for item in content:
            ids.append(item["id"])
            self.assertDictEqualsSchema(
                item,
                SnapOutput.from_orm(Snap.objects.get(id=item["id"])),
            )

        if expected_number >= 1:
            self.assertIn(str(snap_3.id), ids)
        if expected_number >= 2:
            self.assertIn(str(snap_2.id), ids)
        if expected_number >= 3:
            self.assertIn(str(snap_1.id), ids)

    def test_list_snaps(self):
        self._do_test_list_snaps(None, 3)

    def test_list_snaps_with_since_old(self):
        d1 = datetime.now(tz=timezone.utc) - timedelta(days=4)
        self._do_test_list_snaps(d1, 3)

    def test_list_snaps_with_since_not_that_old(self):
        d2 = datetime.now(tz=timezone.utc) - timedelta(days=1)
        self._do_test_list_snaps(d2, 2)

    def test_list_snaps_with_since_recent(self):
        d3 = datetime.now(tz=timezone.utc) - timedelta(minutes=2)
        self._do_test_list_snaps(d3, 1)

    def test_generate_presigned_url(self):
        data = {
            "id": self.collection_1.id,
            "filename": "image.png",
            "content_type": "application/png",
        }

        kwargs = {}
        response = self.client.post(
            reverse("api:generate_presigned_url", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertIsNotNone(content["object_name"])
        self.assertIsNotNone(content["presigned_url"])
