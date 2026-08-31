import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def get_upload_root() -> Path:
    upload_root = Path(settings.UPLOAD_DIR)
    if not upload_root.is_absolute():
        upload_root = Path(__file__).resolve().parents[2] / upload_root
    upload_root.mkdir(parents=True, exist_ok=True)
    return upload_root


class LocalStorage:

    @staticmethod
    async def upload_product_image(file: UploadFile) -> str:
        upload_dir = get_upload_root() / "products"
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = file.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = upload_dir / filename

        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        site_url = settings.SITE_URL.rstrip("/")
        return f"{site_url}/uploads/products/{filename}"

    @staticmethod
    async def upload_cms_image(file: UploadFile) -> str:
        upload_dir = get_upload_root() / "cms"
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = file.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = upload_dir / filename

        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        site_url = settings.SITE_URL.rstrip("/")
        return f"{site_url}/uploads/cms/{filename}"


local_storage = LocalStorage()
