import uuid
import os
import boto3
from .interface import ImageSaverInterface, ImageSaverError


class S3ImageSaver(ImageSaverInterface):
    def __init__(self, config_loader):
        super().__init__(config_loader)
        
        s3_config = self._config.get("s3", {})
        self._bucket = s3_config.get("bucket")
        self._region = s3_config.get("region", "us-east-1")
        self._path_prefix = s3_config.get("path_prefix", "")
        
        if not self._bucket:
            raise ImageSaverError("S3 bucket not configured")
        
        access_key_env = s3_config.get("aws_access_key_id_env", "AWS_ACCESS_KEY_ID")
        secret_key_env = s3_config.get("aws_secret_access_key_env", "AWS_SECRET_ACCESS_KEY")
        
        aws_access_key_id = os.getenv(access_key_env)
        aws_secret_access_key = os.getenv(secret_key_env)
        
        self._s3_client = boto3.client(
            's3',
            region_name=self._region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def save(self, image_bytes: bytes, name_hint: str = None) -> str:
        unique_id = uuid.uuid4().hex
        if name_hint:
            safe_hint = "".join(c if c.isalnum() or c in "-_" else "-" for c in name_hint)
            filename = f"{safe_hint}_{unique_id}"
        else:
            filename = unique_id

        extension = self._detect_extension(image_bytes)
        full_filename = f"{filename}.{extension}" if extension else filename

        s3_key = f"{self._path_prefix}/{full_filename}" if self._path_prefix else full_filename

        try:
            self._s3_client.put_object(
                Bucket=self._bucket,
                Key=s3_key,
                Body=image_bytes,
                ContentType=self._get_content_type(extension)
            )
        except Exception as e:
            raise ImageSaverError(f"Failed to upload to S3: {e}") from e

        return f"s3://{self._bucket}/{s3_key}"

    def _get_content_type(self, extension: str) -> str:
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp"
        }
        return content_types.get(extension, "application/octet-stream")