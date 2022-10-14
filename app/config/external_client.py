from unittest.mock import Mock

from config import settings
from config.s3_client import S3Client

if settings.S3_ENV.lower() == "mock":
    s3_client = Mock(spec=S3Client)
    s3_client.generate_object_name.return_value = "object_name"
    s3_client.generate_presigned_url.return_value = "presigned_url"
    s3_client.generate_presigned_upload.return_value = "presigned_url_upload"
else:
    s3_client = S3Client(
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
        bucket_name=settings.AWS_BUCKET_NAME,
    )
