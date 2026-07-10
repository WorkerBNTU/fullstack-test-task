import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import STORAGE_DIR
from src.models import StoredFile
from src.repositories.file_repository import FileRepository

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

_UPLOAD_CHUNK_SIZE = 1 << 20  # 1 MiB


class FileService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = FileRepository(session)

    async def list_files(self) -> list[StoredFile]:
        return await self._repo.list_all()

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self._repo.get(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = STORAGE_DIR / stored_name

        # Stream to disk in chunks instead of reading the whole upload into
        # memory first -- avoids buffering the entire file for large uploads.
        size = 0
        with stored_path.open("wb") as destination:
            while chunk := await upload_file.read(_UPLOAD_CHUNK_SIZE):
                destination.write(chunk)
                size += len(chunk)

        if size == 0:
            stored_path.unlink(missing_ok=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=(
                upload_file.content_type
                or mimetypes.guess_type(stored_name)[0]
                or "application/octet-stream"
            ),
            size=size,
            processing_status="uploaded",
        )
        return await self._repo.add(file_item)

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        return await self._repo.save(file_item)

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        stored_path = STORAGE_DIR / file_item.stored_name
        if stored_path.exists():
            stored_path.unlink()
        await self._repo.delete(file_item)

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
            )
        return file_item, stored_path
