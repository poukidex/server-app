from collection.api.collections import CollectionAPI
from core.tests.base import BaseTest
from viewsets.tests.abstract import APIViewSetTest, Credentials, Payloads
from viewsets.tests.create import CreateAPIViewTest
from viewsets.tests.delete import DeleteAPIViewTest
from viewsets.tests.list import ListAPIViewTest
from viewsets.tests.retrieve import RetrieveAPIViewTest
from viewsets.tests.update import UpdateAPIViewTest


class CollectionAPITestResource(APIViewSetTest, BaseTest):
    api = CollectionAPI

    def get_instance(self):
        return self.first_collection

    payloads = Payloads(
        ok={"name": "name", "description": "description"},
        bad_request={"name": "name"},
        conflict={"name": "second-collection", "description": "description"},
    )

    list = ListAPIViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    create = CreateAPIViewTest(
        payloads=payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    retrieve = RetrieveAPIViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    update = UpdateAPIViewTest(
        payloads=payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )
    delete = DeleteAPIViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )
