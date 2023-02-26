from datetime import datetime, timedelta

from .abstract_client import AbstractClient
from google.cloud import storage
from django.core.cache import cache


class GoogleClient(AbstractClient):
    client: storage.Client
    bucket_name: str

    def __init__(self, secret_json_path: str, bucket_name: str):
        self.client = storage.Client.from_service_account_json(secret_json_path)
        self.bucket_name = bucket_name

    def get_object(self, object_name: str):
        return (
            self.client.get_bucket(self.bucket_name)
            .get_blob(object_name)
            .download_as_string()
        )

    def delete_object(self, object_name: str):
        return self.client.get_bucket(self.bucket_name).get_blob(object_name).delete()

    def copy_object(self, source_object_name: str, destination_object_name: str):
        bucket = self.client.get_bucket(self.bucket_name)
        source_blob = bucket.blob(source_object_name)
        return bucket.copy_blob(source_blob, bucket, new_name=destination_object_name)

    def generate_presigned_url(self, object_name: str, expiration: int = 3600):
        cache_key = f"s3_presigned_url:{object_name}"
        presigned_url = cache.get(cache_key)
        if presigned_url is not None:
            return presigned_url

        presigned_url = (
            self.client
            .get_bucket(self.bucket_name)
            .blob(object_name)
            .generate_signed_url(
                expiration=(datetime.utcnow() + timedelta(seconds=expiration))
            )
        )
        cache.set(cache_key, presigned_url, expiration)
        return presigned_url

    def generate_presigned_post_url(
        self, object_name: str, file_type: str, expiration: int = 3600
    ):
        return self.client.generate_signed_post_policy_v4(
            bucket_name=self.bucket_name,
            blob_name=object_name,
            expiration=(datetime.utcnow() + timedelta(seconds=expiration)),
        )

    def close_connection(self):
        self.client.close()
