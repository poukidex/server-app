import json
import logging

from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from ninja import Schema
from orjson import orjson

from config.authentication import JWTCoder
from poukidex.models import Collection, Item, PendingItem, Snap
from userauth.models import Token, User


class BaseTest(TestCase):
    user_one: AbstractUser
    user_one_pwd: str
    token_one: Token

    user_two: AbstractUser
    user_two_pwd: str
    token_two: Token

    user_three: AbstractUser
    user_three_pwd: str
    token_three: Token

    previous_level: int

    second_collection: Collection
    first_collection: Collection

    second_collection_item_1: Item
    second_collection_item_2: Item
    second_collection_item_2_snap_1: Snap
    second_collection_item_2_snap_2: Snap

    second_collection_pending_item: PendingItem

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
        cls.user_three_pwd = "password-three"

        cls.user_one = User.objects.create_user(
            username="user-one",
            password=cls.user_one_pwd,
            email="user-one@picsellia.com",
        )
        cls.token_one = Token.objects.create(user=cls.user_one)
        cls.user_two = User.objects.create_user(
            username="user-two",
            password=cls.user_two_pwd,
            email="user-two@picsellia.com",
        )
        cls.token_two = Token.objects.create(user=cls.user_two)
        cls.user_three = User.objects.create_user(
            username="user-three",
            password=cls.user_three_pwd,
            email="user-three@picsellia.com",
        )
        cls.token_three = Token.objects.create(user=cls.user_three)

        cls.auth_user_one = cls._generate_auth_user(cls.token_one)
        cls.auth_user_two = cls._generate_auth_user(cls.token_two)
        cls.auth_user_three = cls._generate_auth_user(cls.token_three)

        cls.first_collection = Collection.objects.create(
            creator=cls.user_one,
            name="first-collection",
            description="some",
        )

        cls.second_collection = Collection.objects.create(
            creator=cls.user_one,
            name="second-collection",
            description="some",
        )

        cls.second_collection_item_1 = Item.objects.create(
            collection=cls.second_collection,
            name="some-name",
            description="description",
            object_name="object_name",
        )

        cls.second_collection_item_2 = Item.objects.create(
            collection=cls.second_collection,
            name="some-name2",
            description="description",
            object_name="object_name",
        )

        cls.second_collection_pending_item = PendingItem.objects.create(
            collection=cls.second_collection,
            name="some-name3",
            description="description",
            object_name="object_name",
            creator=cls.user_two,
        )

        cls.second_collection_item_2_snap_1 = Snap.objects.create(
            item=cls.second_collection_item_2,
            user=cls.user_one,
            comment="Random comment",
            object_name="some object_name",
        )

        cls.second_collection_item_2_snap_2 = Snap.objects.create(
            item=cls.second_collection_item_2,
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

    @staticmethod
    def _generate_auth_user(token: Token):
        token = JWTCoder.encode(id_token=token.key)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    @staticmethod
    def _generate_auth_user_by_token(token: Token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token.key}"}
