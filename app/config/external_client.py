from unittest.mock import Mock

from config import settings
from config.storage.google_client import GoogleClient
from core.notification.notifier import Notifier

if settings.S3_ENV.lower() == "mock":
    s3_client = Mock(spec=GoogleClient)
    s3_client.generate_presigned_url.return_value = "presigned_url"
    s3_client.generate_presigned_post_url.return_value = {
        "url": "some_url",
        "fields": {},
    }
else:
    s3_client = GoogleClient(
        secret_json_path=settings.GCP_SECRETS_PATH, bucket_name=settings.GCP_BUCKET_NAME
    )


if settings.FCM_ENV.lower() == "mock":
    notifier = Mock(spec=Notifier)

else:
    notifier = Notifier()
