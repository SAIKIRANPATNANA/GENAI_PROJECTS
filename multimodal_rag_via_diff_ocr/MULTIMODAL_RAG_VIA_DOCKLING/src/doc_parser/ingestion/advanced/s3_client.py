"""Async S3 client for downloading documents."""

from io import BytesIO
from typing import TYPE_CHECKING

import aioboto3

from .config import settings
from .logging import get_logger

if TYPE_CHECKING:
    from aioboto3.session import Session

logger = get_logger("s3_client")


class S3Client:
    """Async S3 client wrapper using aioboto3."""

    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self.region = settings.aws_region
        self._session: "Session" | None = None

    async def _get_session(self) -> "Session":
        if self._session is None:
            self._session = aioboto3.Session()
        return self._session

    async def download(self, s3_key: str) -> bytes:
        """Download a file from S3 and return its contents."""
        session = await self._get_session()
        async with session.client("s3", region_name=self.region) as client:
            logger.info("Downloading from S3", bucket=self.bucket, key=s3_key)
            response = await client.get_object(Bucket=self.bucket, Key=s3_key)
            async with response["Body"] as stream:
                data = await stream.read()
            logger.info("Downloaded from S3", bucket=self.bucket, key=s3_key, size=len(data))
            return data

    async def upload(self, local_path: str, s3_key: str) -> None:
        """Upload a local file to S3."""
        session = await self._get_session()
        async with session.client("s3", region_name=self.region) as client:
            logger.info("Uploading to S3", bucket=self.bucket, key=s3_key, local_path=local_path)
            await client.upload_file(local_path, self.bucket, s3_key)
            logger.info("Uploaded to S3", bucket=self.bucket, key=s3_key)

    async def upload_bytes(self, data: bytes, s3_key: str) -> None:
        """Upload raw bytes to S3."""
        session = await self._get_session()
        async with session.client("s3", region_name=self.region) as client:
            from io import BytesIO
            logger.info("Uploading bytes to S3", bucket=self.bucket, key=s3_key, size=len(data))
            await client.upload_fileobj(BytesIO(data), self.bucket, s3_key)
            logger.info("Uploaded bytes to S3", bucket=self.bucket, key=s3_key)

    async def list_keys(self, prefix: str) -> list[str]:
        """List S3 keys under a prefix."""
        session = await self._get_session()
        keys: list[str] = []
        async with session.client("s3", region_name=self.region) as client:
            paginator = client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
        return keys


async def download_s3_document(s3_key: str) -> BytesIO:
    """Convenience function: download S3 key to BytesIO."""
    client = S3Client()
    data = await client.download(s3_key)
    return BytesIO(data)
