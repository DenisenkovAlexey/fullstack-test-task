import hashlib
import logging
import mimetypes
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository

logger = logging.getLogger(__name__)


class FileService:
    """Сервис для управления файлами."""

    def __init__(
        self,
        file_repo: FileRepository,
        alert_repo: AlertRepository,
        storage_dir: Path,
    ) -> None:
        self._file_repo = file_repo
        self._alert_repo = alert_repo
        self._storage_dir = storage_dir

    async def list_files(self, limit: int = 100, offset: int = 0) -> list[StoredFile]:
        return list(await self._file_repo.get_all(limit=limit, offset=offset))

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self._file_repo.get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        content = await upload_file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        content_hash = hashlib.sha256(content).hexdigest()

        # Проверяем, существует ли уже файл с таким хэшем
        existing = await self._file_repo.get_by_content_hash(content_hash)
        if existing:
            logger.info("File with hash %s already exists: %s", content_hash, existing.id)
            return existing

        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = self._storage_dir / stored_name

        # Атомарная запись
        try:
            with tempfile.NamedTemporaryFile(dir=self._storage_dir, delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            tmp_path.replace(stored_path)
        except Exception:
            logger.exception("Failed to write file %s", stored_name)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save file")

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
            size=len(content),
            processing_status="uploaded",
            content_hash=content_hash,
        )
        try:
            return await self._file_repo.add(file_item)
        except Exception:
            stored_path.unlink(missing_ok=True)
            logger.exception("Failed to create file record for %s", file_id)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create file record")

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self._file_repo.get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        file_item.title = title
        await self._file_repo._session.commit()
        await self._file_repo._session.refresh(file_item)
        return file_item

    async def delete_file(self, file_id: str) -> None:
        file_item = await self._file_repo.get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        stored_name = file_item.stored_name
        await self._file_repo.delete(file_item)

        stored_path = self._storage_dir / stored_name
        if stored_path.exists():
            stored_path.unlink()
            logger.info("Deleted stored file %s", stored_name)

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        stored_path = self._storage_dir / file_item.stored_name
        if not stored_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
        return file_item, stored_path
