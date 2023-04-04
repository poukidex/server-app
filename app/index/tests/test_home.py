from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from django.urls import reverse

from config.tests.base_test import BaseTest
from index.models import Proposition, Publication
from index.schemas import PropositionSchema


class TestHome(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.publication_another = Publication.objects.create(
            index=cls.second_index,
            name="another-publication",
            description="description",
            object_name="object_name",
        )

    def _do_test_list_propositions(self, since_datetime, expected_number):
        Proposition.objects.all().delete()

        d1 = datetime.now(tz=timezone.utc) - timedelta(days=2)
        proposition_1 = Proposition.objects.create(
            publication=self.publication_another,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
            created_at=d1,
        )

        d2 = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
        proposition_2 = Proposition.objects.create(
            publication=self.second_index_publication_2,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
            created_at=d2,
        )

        d3 = datetime.now(tz=timezone.utc)
        proposition_3 = Proposition.objects.create(
            publication=self.second_index_publication_1,
            user=self.user_one,
            comment="Random comment",
            object_name="some object_name",
            created_at=d3,
        )

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
                PropositionSchema.from_orm(Proposition.objects.get(id=item["id"])),
            )

        if expected_number >= 1:
            self.assertIn(str(proposition_3.id), ids)
        if expected_number >= 2:
            self.assertIn(str(proposition_2.id), ids)
        if expected_number >= 3:
            self.assertIn(str(proposition_1.id), ids)

    def test_list_propositions(self):
        self._do_test_list_propositions(None, 3)

    def test_list_propositions_with_since_old(self):
        d1 = datetime.now(tz=timezone.utc) - timedelta(days=4)
        self._do_test_list_propositions(d1, 3)

    def test_list_propositions_with_since_not_that_old(self):
        d2 = datetime.now(tz=timezone.utc) - timedelta(days=1)
        self._do_test_list_propositions(d2, 2)

    def test_list_propositions_with_since_recent(self):
        d3 = datetime.now(tz=timezone.utc) - timedelta(minutes=2)
        self._do_test_list_propositions(d3, 1)

    def test_generate_presigned_url(self):
        data = {
            "id": self.first_index.id,
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
