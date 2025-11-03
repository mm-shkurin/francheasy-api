from app.core.config import MinioSettings
import boto3
import uuid
import json
from fastapi import UploadFile
import asyncio
from typing import Optional

minio_settings = MinioSettings()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=minio_settings.minio_root_user,
            aws_secret_access_key=minio_settings.minio_root_password,
            endpoint_url=minio_settings.minio_endpoint_url
        )
        
        self.bucket = minio_settings.minio_bucket_name
        endpoint_url = str(minio_settings.minio_endpoint_url)
        if endpoint_url.startswith('http://'):
            self.base_url = endpoint_url.replace('http://', 'https://').rstrip('/')
        else:
            self.base_url = endpoint_url.rstrip('/')
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except self.s3_client.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.s3_client.create_bucket(Bucket=self.bucket)
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket,
                    Policy=json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{self.bucket}/*"]
                            }
                        ]
                    })
                )
            else:
                raise

    def _generate_key(self, car_id: str, filename: Optional[str], folder: str) -> str:
        ext = ""
        if filename and "." in filename:
            ext = filename.split(".")[-1]
        unique = uuid.uuid4().hex
        suffix = f".{ext}" if ext else ""
        return f"{car_id}/{folder}/{unique}{suffix}"
    
    async def upload_file(self, car_id: str, file: UploadFile, folder: str = "photos") -> str:
        key = self._generate_key(car_id, file.filename, folder)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.upload_fileobj(
                file.file,
                self.bucket,
                key,
                ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
            ),
        )

        return f"{self.base_url}/{self.bucket}/{key}"

    def make_url(self, key: str) -> str:
        return f"{self.base_url}/{self.bucket}/{key}"

    def extract_key_from_url(self, url: str) -> str:
        prefix = f"{self.base_url}/{self.bucket}/"
        return url[len(prefix):] if url.startswith(prefix) else url

    async def upload_file_get_key(self, car_id: str, file: UploadFile, folder: str = "photos") -> str:
        key = self._generate_key(car_id, file.filename, folder)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.upload_fileobj(
                file.file,
                self.bucket,
                key,
                ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
            ),
        )
        return key

    async def upload_file_from_bytes(self, car_id: str, file_bytes: bytes, filename: Optional[str] = None, content_type: Optional[str] = None, folder: str = "photos") -> str:
        key = self._generate_key(car_id, filename, folder)

        extra_args = {"ACL": "public-read"}
        if content_type:
            extra_args["ContentType"] = content_type

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes,
                **extra_args,
            ),
        )

        return f"{self.base_url}/{self.bucket}/{key}"

    async def save_photos_json(self, car_id: str, urls: list, folder: str = "photos") -> str:
        key = f"{car_id}/{folder}/photos.json"
        body = json.dumps({"photos": urls})

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ACL="public-read",
                ContentType="application/json",
            ),
        )

        return f"{self.base_url}/{self.bucket}/{key}"

    async def get_file_by_key(self, key: str):
        
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=self.bucket, Key=key)
            )
            file_bytes = result['Body'].read()
            content_type = result.get('ContentType', 'application/octet-stream')
            return file_bytes, content_type
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File with key {key} not found")
    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            lambda: self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
        )
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        url = url.replace(':9000', '')
        return url

s3_service = S3Service()