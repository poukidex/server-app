from http import HTTPStatus
from uuid import UUID

from django.db.models import Count, Q
from ninja import Query, Router, Schema
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import update_object_from_schema
from index.models import Approbation, Proposition
from index.schemas import (
    ApprobationInput,
    ApprobationQuery,
    ApprobationSchema,
    PropositionSchema,
    PropositionUpdate,
)

router = Router()


@router.get(
    path="/{id}",
    url_name="proposition",
    response={HTTPStatus.OK: PropositionSchema},
    operation_id="get_capture",
)
def retrieve_proposition(request, id: UUID):
    return HTTPStatus.OK, Proposition.objects.annotate(
        nb_likes=Count("approbations", filter=Q(approbations__approved=True)),
        nb_dislikes=Count("approbations", filter=Q(approbations__approved=False)),
    ).get(id=id)


@router.put(
    path="/{id}",
    url_name="proposition",
    response={HTTPStatus.OK: PropositionSchema},
    operation_id="update_capture",
)
def update_proposition(request, id: UUID, payload: PropositionUpdate):
    proposition: Proposition = Proposition.objects.select_related(
        "publication__index"
    ).get(id=id)

    if (
        proposition.user != request.user
        and proposition.publication.index.creator != request.user
    ):
        raise ForbiddenException()

    update_object_from_schema(proposition, payload)

    return HTTPStatus.OK, proposition


@router.delete(
    path="/{id}",
    url_name="proposition",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_capture",
)
def delete_proposition(request, id: UUID):
    proposition: Proposition = Proposition.objects.select_related(
        "publication__index"
    ).get(id=id)

    if (
        proposition.user != request.user
        and proposition.publication.index.creator != request.user
    ):
        raise ForbiddenException()

    proposition.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/approve",
    url_name="proposition_approve",
    response={HTTPStatus.OK: ApprobationSchema},
    operation_id="create_reaction",
)
def approve_proposition(request, id: UUID, payload: ApprobationInput):
    proposition: Proposition = Proposition.objects.select_related(
        "publication__index"
    ).get(id=id)

    approbation, _ = Approbation.objects.get_or_create(
        proposition=proposition, user=request.user
    )
    approbation.approved = payload.approved
    approbation.save()

    return HTTPStatus.OK, approbation


@router.get(
    path="/{id}/approbations",
    url_name="proposition_approbations",
    response={HTTPStatus.OK: list[ApprobationSchema]},
    operation_id="get_reaction_list",
)
@paginate(OverpoweredPagination)
def list_approbations(
    request, id: UUID, filters: ApprobationQuery = Query(default=Schema())
):
    filters_dict: dict = filters.dict(exclude_unset=True)
    return Approbation.objects.filter(proposition_id=id, **filters_dict)


@router.get(
    path="/{id}/approbation",
    url_name="approbation",
    response={HTTPStatus.OK: ApprobationSchema},
    operation_id="get_reaction",
)
def get_approbation(request, id: UUID):
    return HTTPStatus.OK, Approbation.objects.get(proposition_id=id, user=request.user)


@router.delete(
    path="/{id}/approbation",
    url_name="approbation",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_reaction",
)
def delete_approbation(request, id: UUID):
    approbation: Approbation = Approbation.objects.get(
        proposition_id=id, user=request.user
    )

    approbation.delete()

    return HTTPStatus.NO_CONTENT, None
