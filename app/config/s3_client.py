import uuid

import boto3


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

    def generate_object_name(self, prefix: str, filename: str):
        # TODO: Check filename
        return f"{prefix}/{uuid.uuid4()}-{filename}"

    def generate_presigned_url(self, object_name, expiration=3600):
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_name,
            },
            ExpiresIn=expiration,
        )

    def generate_presigned_upload(self, object_name, file_type, expiration=3600):
        return self._client.generate_presigned_post(
            Bucket=self.bucket_name,
            Key=object_name,
            Fields={"Content-Type": file_type},
            Conditions=[{"Content-Type": file_type}],
            ExpiresIn=expiration,
        )
