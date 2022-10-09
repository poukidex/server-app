from http import HTTPStatus
from uuid import UUID

from config.exceptions import ForbiddenException, IncoherentInput
from ninja import Router

from index.models import Approbation, Proposition
from index.schemas import ApprobationInput, ExtendedPropositionSchema, PropositionUpdate
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
        or proposition.publication.index.creator != request.user
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
        or proposition.publication.index.creator != request.user
    ):
        raise ForbiddenException()

    proposition.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(path="/{id}/approve", response={HTTPStatus.OK: ExtendedPropositionSchema})
def approve_proposition(request, id: UUID, payload: ApprobationInput):
    proposition: Proposition = (
        Proposition.objects.select_related("publication__index")
        .prefetch_related("approbation__user__picture")
        .get(id=id)
    )

    if proposition.user == request.user:
        raise IncoherentInput("You cannot approve your own proposition!")

    approbation: Approbation = Approbation.objects.get_or_create(
        proposition=proposition, user=request.user
    )
    approbation.approved = payload.approved
    approbation.save()

    return HTTPStatus
