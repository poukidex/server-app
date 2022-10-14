import json
import logging
from datetime import datetime, timedelta, timezone

import jwt
from config import settings
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from ninja import Schema
from orjson import orjson
from userauth.models import User

from index.models import Index, Proposition, Publication
from index.schemas import ValidationMode


class BaseTest(TestCase):
    user_one: AbstractUser
    user_one_pwd: str

    user_two: AbstractUser
    user_two_pwd: str

    previous_level: int

    second_index: Index
    first_index: Index

    second_index_publication_1: Publication
    second_index_publication_2: Publication

    @classmethod
    def setUpClass(cls) -> None:
        super(BaseTest, cls).setUpClass()
        """Reduce the django's log level to avoid warnings and errors"""
        logger = logging.getLogger("django.request")
        cls.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)

    @classmethod
    def setUpTestData(cls):
        super(BaseTest, cls).setUpTestData()
        cls.user_one_pwd = "password-one"
        cls.user_two_pwd = "password-two"

        cls.user_one = User.objects.create_user(
            username="user-one",
            password=cls.user_one_pwd,
            email="user-one@picsellia.com",
        )
        cls.user_two = User.objects.create_user(
            username="user-two",
            password=cls.user_two_pwd,
            email="user-two@picsellia.com",
        )

        cls.auth_user_one = cls._generate_auth_user(cls, cls.user_one)
        cls.auth_user_two = cls._generate_auth_user(cls, cls.user_two)

        cls.first_index = Index.objects.create(
            creator=cls.user_one,
            name="first-index",
            description="some",
            validation_mode=ValidationMode.Manual,
        )

        cls.second_index = Index.objects.create(
            creator=cls.user_one,
            name="second-index",
            description="some",
            validation_mode=ValidationMode.Manual,
        )

        cls.second_index_publication_1 = Publication.objects.create(
            index=cls.second_index,
            name="some-name",
            description="description",
            object_name="object_name",
        )

        cls.second_index_publication_2 = Publication.objects.create(
            index=cls.second_index,
            name="some-name2",
            description="description",
            object_name="object_name",
        )

        cls.second_index_publication_2_proposition_1 = Proposition.objects.create(
            publication=cls.second_index_publication_2,
            user=cls.user_one,
            comment="Random comment",
            object_name="some object_name",
        )

        cls.second_index_publication_2_proposition_2 = Proposition.objects.create(
            publication=cls.second_index_publication_2,
            user=cls.user_two,
            comment="Random comment of user two",
            object_name="some object_name",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super(BaseTest, cls).tearDownClass()
        """Reset the log level back to normal"""
        logger = logging.getLogger("django.request")
        logger.setLevel(cls.previous_level)

    def assertDictEqualsSchema(self, element: dict, schema: Schema):
        copied_element = {}
        for key, value in element.items():
            copied_element[key] = value

        self.assertDictEqual(
            copied_element,
            json.loads(orjson.dumps(schema.dict())),
        )

    def _generate_auth_user(self, user: AbstractUser):
        expires_in = datetime.now(tz=timezone.utc) + timedelta(
            seconds=float(settings.JWT_EXPIRES_IN)
        )
        token = jwt.encode(
            {"user_id": str(user.id), "exp": expires_in},
            settings.JWT_KEY,
            algorithm="HS256",
        )
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
