from http import HTTPStatus
from uuid import UUID

from django.db.models import Count
from ninja import Router
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import check_object, update_object_from_schema
from index.models import Index, PendingPublication, Publication
from index.schemas import (
    IndexInput,
    IndexSchema,
    IndexUpdate,
    PendingPublicationSchema,
    PublicationInput,
    PublicationSchema,
)

router = Router()


@router.get(
    path="",
    response={HTTPStatus.OK: list[IndexSchema]},
    url_name="indexes",
    operation_id="get_collection_list",
)
@paginate(OverpoweredPagination)
def list_indexes(request):
    return Index.objects.annotate(nb_items=Count("publications")).all()


@router.post(
    path="",
    response={HTTPStatus.CREATED: IndexSchema},
    url_name="indexes",
    operation_id="create_collection",
)
def create_index(request, payload: IndexInput):
    index = Index(creator=request.user, **payload.dict())
    check_object(index)
    index.save()

    return HTTPStatus.CREATED, index


@router.get(
    path="/{id}",
    response={HTTPStatus.OK: IndexSchema},
    url_name="index",
    operation_id="get_collection",
)
def retrieve_index(request, id: UUID):
    return HTTPStatus.OK, Index.objects.annotate(nb_items=Count("publications")).get(
        id=id
    )


@router.put(
    path="/{id}",
    response={HTTPStatus.OK: IndexSchema},
    url_name="index",
    operation_id="update_collection",
)
def update_index(request, id: UUID, payload: IndexUpdate):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(index, payload)

    return HTTPStatus.OK, index


@router.delete(
    path="/{id}",
    response={HTTPStatus.NO_CONTENT: None},
    url_name="index",
    operation_id="delete_collection",
)
def delete_index(request, id: UUID):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    index.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/pending-publications",
    response={HTTPStatus.CREATED: PendingPublicationSchema},
    url_name="index_pending_publications",
    operation_id="create_pending_item",
)
def add_pending_publication(request, id: UUID, payload: PublicationInput):
    index = Index.objects.get(id=id)

    pending_publication = PendingPublication(
        index=index, creator=request.user, **payload.dict()
    )

    check_object(pending_publication)

    pending_publication.save()

    return HTTPStatus.CREATED, pending_publication


@router.get(
    path="/{id}/pending-publications",
    response={HTTPStatus.OK: list[PendingPublicationSchema]},
    url_name="index_pending_publications",
    operation_id="list_pending_items",
)
@paginate(OverpoweredPagination)
def list_pending_publications(request, id: UUID):
    index = Index.objects.get(id=id)

    if request.user == index.creator:
        return PendingPublication.objects.filter(index=index)
    else:
        return PendingPublication.objects.filter(index=index, creator=request.user)


@router.post(
    path="/{id}/publications",
    response={HTTPStatus.CREATED: PublicationSchema},
    url_name="index_publications",
    operation_id="create_item",
)
def add_publication(request, id: UUID, payload: PublicationInput):
    index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    publication = Publication(index=index, **payload.dict())

    check_object(publication)

    publication.save()

    return HTTPStatus.CREATED, publication


@router.get(
    path="/{id}/publications",
    response={HTTPStatus.OK: list[PublicationSchema]},
    url_name="index_publications",
    operation_id="get_item_list",
)
@paginate(OverpoweredPagination)
def list_publications(request, id: UUID):
    return Publication.objects.annotate(nb_captures=Count("propositions")).filter(
        index_id=id
    )
