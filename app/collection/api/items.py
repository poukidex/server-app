from django.db.models import Count, Q
from generators.configuration import (
    ChildConfiguration,
    CreateConfiguration,
    DeleteConfiguration,
    GetConfiguration,
    ListConfiguration,
    UpdateConfiguration,
)
from generators.generator import APIGenerator

from core.models.collections import Item, Snap
from core.schemas.collections import ItemOutput, ItemUpdate, SnapInput, SnapSchema


class ItemsAPI(APIGenerator):
    model = Item

    # if item.collection.creator != request.user:
    #     raise ForbiddenException()

    get = GetConfiguration(
        output_schema=ItemOutput, annotate=dict(nb_snaps=Count("snaps"))
    )
    update = UpdateConfiguration(
        input_schema=ItemUpdate,
        output_schema=ItemOutput,
    )
    delete = DeleteConfiguration()

    children = [
        ChildConfiguration(
            model=Snap,
            get=GetConfiguration(
                output_schema=SnapSchema,
                annotate=dict(nb_likes=Count("likes", filter=Q(likes__liked=True))),
            ),
            list=ListConfiguration(
                output_schema=SnapSchema,
                annotate=dict(nb_likes=Count("likes", filter=Q(likes__liked=True))),
            ),
            bulk_create=CreateConfiguration(
                input_schema=SnapInput, output_schema=SnapSchema
            ),
        )
    ]


# @router.get(
#     path="/{id}/snap",
#     url_name="my_snap",
#     response={HTTPStatus.OK: SnapSchema},
#     operation_id="get_my_capture",
# )
# def retrieve_my_snap(request, id: UUID):
#     return HTTPStatus.OK, Snap.objects.get(item_id=id, user=request.user)
