from http import HTTPStatus
from uuid import UUID

from django.db.models import Count

from config.exceptions import ForbiddenException
from ninja import Router
from ninja.pagination import paginate
from config.pagination import OverpoweredPagination

from config.external_client import s3_client
from index.models import Index, Publication
from index.schemas import (
    ExtendedIndexSchema,
    ExtendedPublicationSchema,
    PublicationSchema,
    IndexInput,
    IndexSchema,
    IndexUpdate,
    PublicationInput,
    ImageUploadInput,
    ImageUploadSchema,
)
from index.utils import check_object, update_object_from_schema

router = Router()


@router.get(path="", response={HTTPStatus.OK: list[IndexSchema]}, url_name="indexes", operation_id="get_collection_list")
@paginate(OverpoweredPagination)
def list_indexes(request):
    return Index.objects.annotate(nb_items=Count('publications')).all()


@router.post(
    path="", response={HTTPStatus.CREATED: ExtendedIndexSchema}, url_name="indexes", operation_id="create_collection"
)
def create_index(request, payload: IndexInput):
    index = Index(creator=request.user, **payload.dict())
    check_object(index)
    index.save()

    return HTTPStatus.CREATED, index


@router.get(
    path="/{id}", response={HTTPStatus.OK: ExtendedIndexSchema}, url_name="index", operation_id="get_collection",
)
def retrieve_index(request, id: UUID):
    return HTTPStatus.OK, Index.objects.get(id=id)


@router.put(
    path="/{id}", response={HTTPStatus.OK: ExtendedIndexSchema}, url_name="index", operation_id="update_collection"
)
def update_index(request, id: UUID, payload: IndexUpdate):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(index, payload)

    return HTTPStatus.OK, index


@router.delete(path="/{id}", response={HTTPStatus.NO_CONTENT: None}, url_name="index", operation_id="delete_collection")
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
    operation_id="create_item"
)
def add_publication(request, id: UUID, payload: PublicationInput):
    index: Index = Index.objects.get(id=id)

    if index.creator != request.user:
        raise ForbiddenException()

    publication: Publication = Publication(index_id=id, **payload.dict())

    check_object(publication)

    publication.save()

    return HTTPStatus.CREATED, publication


@router.post(
    path="/{id}/publications/upload",
    url_name="index_publications_upload",
    response={HTTPStatus.OK: ImageUploadSchema},
    operation_id="generate_item_presigned_url"
)
def generate_presigned_url_for_upload(request, id: UUID, payload: ImageUploadInput):
    index: Index = Index.objects.get(id=id)

    object_name = s3_client.generate_object_name(str(index.id), payload.filename)

    presigned_url = s3_client.generate_presigned_upload(
        object_name, payload.content_type
    )

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)


@router.get(
    path="/{id}/publications",
    response={HTTPStatus.OK: list[PublicationSchema]},
    url_name="index_publications",
    operation_id="get_item_list"
)
@paginate(OverpoweredPagination)
def list_publications(request, id: UUID):
    return Publication.objects.filter(index_id=id)
