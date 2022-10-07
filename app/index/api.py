from http import HTTPStatus

from ninja import NinjaAPI

from index.models import Index
from index.schemas import IndexSchema

api = NinjaAPI()


@api.get(path="/indexes", response={HTTPStatus.OK: list[IndexSchema]})
def list_indexes(request):
    return HTTPStatus.OK, Index.objects.all()
