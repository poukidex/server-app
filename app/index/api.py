from http import HTTPStatus
from ninja import NinjaAPI

api = NinjaAPI()


@api.post(
    "indexes",
    response={
        HTTPStatus.NO_CONTENT: None,
        HTTPStatus.UNAUTHORIZED: BaseErrorResponse,
        HTTPStatus.FORBIDDEN: BaseErrorResponse,
        HTTPStatus.CONFLICT: BaseErrorResponse,
        HTTPStatus.UNPROCESSABLE_ENTITY: BaseErrorResponse,
        HTTPStatus.INTERNAL_SERVER_ERROR: BaseErrorResponse,
    },
)
def create_deployment(request: HttpRequest, data: RegisterDeploymentRequest):
    deployment = Deployment(
        id=data.deployment_id,
        host=data.host,
    )
    if data.oracle_host:
        deployment.oracle_host = data.oracle_host

    if data.thresholds:
        if len(data.thresholds) == 1:
            data.thresholds.append(1.0)
        if len(data.thresholds) != 2:
            raise HttpError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Threshold should be either min or min and max",
            )
        deployment.thresholds = data.thresholds
    try:
        deployment.save()
    except django.db.IntegrityError:
        raise HttpError(HTTPStatus.CONFLICT, "Already exists")

    return HTTPStatus.NO_CONTENT, None
