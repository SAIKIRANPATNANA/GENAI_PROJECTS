"""S3 folder uploader utility for pre-ingestion."""

import asyncio
from pathlib import Path

from .config import settings
from .logging import get_logger
from .s3_client import S3Client

logger = get_logger("s3_uploader")

SUPPORTED_EXTENSIONS = {
    ".pdf", ".doc", ".docx",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif",
}


async def upload_folder(local_path: Path, s3_prefix: str | None = None) -> list[str]:
    """Upload all supported files from a local folder to S3.

    Args:
        local_path: Path to local folder containing documents.
        s3_prefix: Optional S3 prefix (defaults to settings.s3_prefix).

    Returns:
        List of uploaded S3 keys.
    """
    prefix = s3_prefix or settings.s3_prefix
    client = S3Client()
    files = [
        f for f in local_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    logger.info("Found files to upload", count=len(files), folder=str(local_path))

    uploaded_keys: list[str] = []
    semaphore = asyncio.Semaphore(10)

    async def _upload_one(file: Path) -> str:
        async with semaphore:
            s3_key = f"{prefix}{file.name}"
            await client.upload(str(file), s3_key)
            return s3_key

    results = await asyncio.gather(*[_upload_one(f) for f in files], return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.error("Upload failed", error=str(result))
        else:
            uploaded_keys.append(result)

    logger.info("Upload complete", uploaded=len(uploaded_keys), failed=len(results) - len(uploaded_keys))
    return uploaded_keys
