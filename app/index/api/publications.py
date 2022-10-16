from http import HTTPStatus
from uuid import UUID

from config.exceptions import ForbiddenException
from config.external_client import s3_client
from ninja import Router

from index.models import Proposition, Publication
from index.schemas import (
    ExtendedPropositionSchema,
    ExtendedPublicationSchema,
    ImageUploadInput,
    ImageUploadSchema,
    PropositionInput,
    PublicationUpdate,
)
from index.utils import check_object, update_object_from_schema

router = Router()


@router.get(
    path="/{id}",
    url_name="publication",
    response={HTTPStatus.OK: ExtendedPublicationSchema},
)
def retrieve_publication(request, id: UUID):
    return HTTPStatus.OK, Publication.objects.get(id=id)


@router.put(
    path="/{id}",
    url_name="publication",
    response={HTTPStatus.OK: ExtendedPublicationSchema},
)
def update_publication(request, id: UUID, payload: PublicationUpdate):
    publication: Publication = Publication.objects.select_related("index").get(id=id)

    if publication.index.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(publication, payload)

    return HTTPStatus.OK, publication


@router.delete(
    path="/{id}", url_name="publication", response={HTTPStatus.NO_CONTENT: None}
)
def delete_publication(request, id: UUID):
    publication: Publication = Publication.objects.select_related("index").get(id=id)

    if publication.index.creator != request.user:
        raise ForbiddenException()

    publication.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/propositions/upload",
    url_name="publication_propositions_upload",
    response={HTTPStatus.OK: ImageUploadSchema},
)
def generate_presigned_url_for_upload(request, id: UUID, payload: ImageUploadInput):
    publication: Publication = Publication.objects.get(id=id)

    object_name = s3_client.generate_object_name(str(publication.id), payload.filename)

    presigned_url = s3_client.generate_presigned_upload(
        object_name, payload.content_type
    )

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)


@router.post(
    path="/{id}/propositions",
    url_name="publication_propositions",
    response={HTTPStatus.CREATED: ExtendedPropositionSchema},
)
def add_proposition(request, id: UUID, payload: PropositionInput):
    publication: Publication = Publication.objects.get(id=id)

    proposition: Proposition = Proposition(
        publication=publication,
        user=request.user,
        object_name=payload.object_name,
        comment=payload.comment,
    )

    check_object(proposition)

    proposition.save()

    return HTTPStatus.CREATED, proposition


@router.get(
    path="/{id}/propositions",
    url_name="publication_propositions",
    response={HTTPStatus.OK: list[ExtendedPropositionSchema]},
)
def list_propositions(request, id: UUID):
    return HTTPStatus.OK, Proposition.objects.filter(publication_id=id)