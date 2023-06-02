from collection.api.collections import CollectionViewSet
from core.tests.base import BaseTest
from viewsets.tests.abstract import Credentials, ModelViewSetTest, Payloads
from viewsets.tests.create import CreateModelViewTest
from viewsets.tests.delete import DeleteModelViewTest
from viewsets.tests.list import ListModelViewTest
from viewsets.tests.retrieve import RetrieveModelViewTest
from viewsets.tests.update import UpdateModelViewTest


class CollectionViewSetTest(ModelViewSetTest, BaseTest):
    model_view_set = CollectionViewSet

    def get_instance(self):
        return self.first_collection

    collection_payloads = Payloads(
        ok={"name": "name", "description": "description"},
        bad_request={"name": "name"},
        conflict={"name": "second-collection", "description": "description"},
    )

    list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    create = CreateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    update = UpdateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )
    delete = DeleteModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )

    item_payloads = Payloads(
        ok={"name": "name", "description": "description", "object_name": "object_name"},
        bad_request={"name": "name"},
        conflict={
            "name": "first-item",
            "description": "description",
            "object_name": "object_name",
        },
    )

    list_items = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(ok=self.auth_user_one),
    )
    create_item = CreateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=lambda self: Credentials(
            ok=self.auth_user_one, forbidden=self.auth_user_two
        ),
    )
