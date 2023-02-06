import uuid

import boto3
from django.core.cache import cache


class S3Client:
    def __init__(
        self,
        region_name,
        aws_access_key_id,
        aws_secret_access_key,
        endpoint_url,
        bucket_name,
    ):
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket_name = bucket_name

    @staticmethod
    def generate_object_name(prefix: str, filename: str):
        # TODO: Check filename
        return f"{prefix}/{uuid.uuid4()}-{filename}"

    def generate_presigned_url(self, object_name, expiration=3600):
        cache_key = f"s3_presigned_url:{object_name}"
        try:
            presigned_url = cache.get(cache_key)
        except Exception:
            presigned_url = None

        if presigned_url is not None:
            return presigned_url
        else:
            presigned_url = self._client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                },
                ExpiresIn=expiration,
            )
            cache.set(cache_key, presigned_url, expiration)
            return presigned_url

    def generate_presigned_upload(self, object_name, file_type, expiration=3600):
        return self._client.generate_presigned_post(
            Bucket=self.bucket_name,
            Key=object_name,
            Fields={"Content-Type": file_type},
            Conditions=[{"Content-Type": file_type}],
            ExpiresIn=expiration,
        )
