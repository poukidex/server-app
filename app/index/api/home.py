from datetime import datetime
from http import HTTPStatus
from typing import Optional

from django.db.models import Count, Q
from ninja import Router
from ninja.pagination import paginate

from config.pagination import OverpoweredPagination
from index.models import Proposition
from index.schemas import PropositionSchema

router = Router()


@router.get(
    path="/feed",
    url_name="feed",
    response={HTTPStatus.OK: list[PropositionSchema]},
    operation_id="get_feeed",
)
@paginate(OverpoweredPagination)
def retrieve_feed(request, since: Optional[datetime] = None):
    propositions = Proposition.objects.select_related("publication__index").annotate(
        nb_likes=Count("approbations", filter=Q(approbations__approved=True)),
    )

    if since:
        propositions = propositions.filter(created_at__gt=since)

    return propositions
