from http import HTTPStatus
from uuid import UUID

from config.exceptions import ForbiddenException
from ninja import Router

from index.models import Proposition
from index.schemas import ExtendedPropositionSchema, PropositionUpdate
from index.utils import update_object_from_schema

router = Router()


@router.get(path="/{id}", response={HTTPStatus.OK: ExtendedPropositionSchema})
def retrieve_proposition(request, id: UUID):
    return HTTPStatus.OK, Proposition.objects.get(id=id)


@router.post(path="/{id}", response={HTTPStatus.OK: ExtendedPropositionSchema})
def update_proposition(request, id: UUID, payload: PropositionUpdate):
    proposition: Proposition = Proposition.objects.select_related(
        "publication__index"
    ).get(id=id)

    if (
        proposition.user != request.user
        or proposition.publication.index.created_by != request.user
    ):
        raise ForbiddenException()

    update_object_from_schema(proposition, payload)

    return HTTPStatus.OK, proposition


@router.delete(path="/{id}", response={HTTPStatus.NO_CONTENT: None})
def delete_proposition(request, id: UUID):
    proposition: Proposition = Proposition.objects.select_related(
        "publication__index"
    ).get(id=id)

    if (
        proposition.user != request.user
        or proposition.publication.index.created_by != request.user
    ):
        raise ForbiddenException()

    proposition.delete()

    return HTTPStatus.NO_CONTENT, None
