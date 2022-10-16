from http import HTTPStatus
from uuid import UUID
from typing import List
from config.exceptions import ForbiddenException
from ninja import Router
from ninja.pagination import paginate
from config.pagination import OverpoweredPagination

from index.models import Index, Publication
from index.schemas import (
    ExtendedIndexSchema,
    ExtendedPublicationSchema,
    IndexInput,
    IndexSchema,
    IndexUpdate,
    PublicationInput,
)
from index.utils import check_object, update_object_from_schema

router = Router()


@router.get(path="", response={HTTPStatus.OK: list[IndexSchema]}, url_name="indexes", operation_id="get_collection_list")
@paginate(OverpoweredPagination)
def list_indexes(request):
    return Index.objects.all()


@router.post(
    path="", response={HTTPStatus.CREATED: ExtendedIndexSchema}, url_name="indexes"
)
def create_index(request, payload: IndexInput):
    index = Index(creator=request.user, **payload.dict())

    check_object(index)

    index.save()

    return HTTPStatus.CREATED, index


@router.get(
    path="/{id}", response={HTTPStatus.OK: ExtendedIndexSchema}, url_name="index"
)
def retrieve_index(request, id: UUID):
    return HTTPStatus.OK, Index.objects.get(id=id)


@router.put(
    path="/{id}", response={HTTPStatus.OK: ExtendedIndexSchema}, url_name="index"
)
def update_index(request, id: UUID, payload: IndexUpdate):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(index, payload)

    return HTTPStatus.OK, index


@router.delete(path="/{id}", response={HTTPStatus.NO_CONTENT: None}, url_name="index")
def delete_index(request, id: UUID):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    index.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/publications",
    response={HTTPStatus.CREATED: ExtendedPublicationSchema},
    url_name="index_publications",
)
def add_publication(request, id: UUID, payload: PublicationInput):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    publication: Publication = Publication(index=index, **payload.dict())

    check_object(publication)

    publication.save()

    return HTTPStatus.CREATED, publication


@router.get(
    path="/{id}/publications",
    response={HTTPStatus.OK: list[ExtendedPublicationSchema]},
    url_name="index_publications",
)
def list_publications(request, id: UUID):
    return HTTPStatus.OK, Publication.objects.filter(index_id=id)
