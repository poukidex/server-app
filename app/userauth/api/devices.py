from http import HTTPStatus

from ninja import Router
from push_notifications.models import GCMDevice

from core.schemas import ErrorOutput
from userauth.schemas import DeviceInput, DeviceOutput

router = Router()


@router.post(
    "",
    response={
        HTTPStatus.CREATED: DeviceOutput,
        HTTPStatus.FORBIDDEN: ErrorOutput,
        HTTPStatus.NOT_FOUND: ErrorOutput,
    },
    url_name="devices",
    operation_id="register_device",
    summary="Register a device",
)
def api_register_devices(request, payload: DeviceInput):
    return HTTPStatus.CREATED, GCMDevice.objects.create(
        registration_id=payload.token, cloud_message_type="FCM", user=request.user
    )
