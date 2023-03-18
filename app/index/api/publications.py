from http import HTTPStatus
from uuid import UUID

from django.db.models import Count, Q
from ninja import Router
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import check_object, update_object_from_schema
from index.models import Proposition, Publication
from index.schemas import (
    PropositionInput,
    PropositionSchema,
    PublicationSchema,
    PublicationUpdate,
)

router = Router()


@router.get(
    path="/{id}",
    url_name="publication",
    response={HTTPStatus.OK: PublicationSchema},
    operation_id="get_item",
)
def retrieve_publication(request, id: UUID):
    return HTTPStatus.OK, Publication.objects.annotate(
        nb_captures=Count("propositions")
    ).get(id=id)


@router.put(
    path="/{id}",
    url_name="publication",
    response={HTTPStatus.OK: PublicationSchema},
    operation_id="update_item",
)
def update_publication(request, id: UUID, payload: PublicationUpdate):
    publication: Publication = Publication.objects.select_related("index").get(id=id)

    if publication.index.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(publication, payload)

    return HTTPStatus.OK, publication


@router.delete(
    path="/{id}",
    url_name="publication",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_item",
)
def delete_publication(request, id: UUID):
    publication: Publication = Publication.objects.select_related("index").get(id=id)

    if publication.index.creator != request.user:
        raise ForbiddenException()

    publication.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/propositions",
    url_name="publication_propositions",
    response={HTTPStatus.CREATED: PropositionSchema},
    operation_id="create_capture",
)
def add_proposition(request, id: UUID, payload: PropositionInput):
    # Assert publication exists
    Publication.objects.get(id=id)

    proposition: Proposition = Proposition(
        publication_id=id, user=request.user, **payload.dict()
    )

    check_object(proposition)

    proposition.save()

    return HTTPStatus.CREATED, proposition


@router.get(
    path="/{id}/proposition",
    url_name="my_proposition",
    response={HTTPStatus.OK: PropositionSchema},
    operation_id="get_my_capture",
)
def retrieve_my_proposition(request, id: UUID):
    return HTTPStatus.OK, Proposition.objects.get(publication_id=id, user=request.user)


@router.get(
    path="/{id}/propositions",
    url_name="publication_propositions",
    response={HTTPStatus.OK: list[PropositionSchema]},
    operation_id="get_capture_list",
)
@paginate(OverpoweredPagination)
def list_propositions(request, id: UUID):
    return Proposition.objects.annotate(
        nb_likes=Count("approbations", filter=Q(approbations__approved=True)),
    ).filter(publication_id=id)
