from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile


class FileRepository:
    """Репозиторий для работы с файлами."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, file_id: str) -> StoredFile | None:
        return await self._session.get(StoredFile, file_id)

    async def get_all(self) -> Sequence[StoredFile]:
        result = await self._session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return result.scalars().all()

    async def add(self, file_item: StoredFile) -> StoredFile:
        self._session.add(file_item)
        await self._session.commit()
        await self._session.refresh(file_item)
        return file_item

    async def delete(self, file_item: StoredFile) -> None:
        await self._session.delete(file_item)
        await self._session.commit()

    async def exists_by_stored_name(self, stored_name: str) -> bool:
        result = await self._session.execute(
            select(StoredFile.id).where(StoredFile.stored_name == stored_name)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_content_hash(self, content_hash: str) -> StoredFile | None:
        result = await self._session.execute(
            select(StoredFile).where(StoredFile.content_hash == content_hash)
        )
        return result.scalar_one_or_none()
