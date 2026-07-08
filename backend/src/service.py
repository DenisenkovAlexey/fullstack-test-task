import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.session import async_session_maker
from src.models import StoredFile, Alert
from src.services.service_factory import ServiceFactory

logger = logging.getLogger(__name__)


async def list_files() -> list[StoredFile]:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="file", session=session).list_files()



async def list_alerts() -> list[Alert]:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="alert", session=session).list_alerts()


async def get_file(file_id: str) -> StoredFile:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="file", session=session).get_file(file_id)



async def create_file(title: str, upload_file: UploadFile) -> StoredFile:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="file", session=session).create_file(title, upload_file)


async def update_file(file_id: str, title: str) -> StoredFile:
    async with async_session_maker() as session:
        file_service = ServiceFactory.get_service(name="file", session=session)
        file_item = await file_service.get_file(file_id)
        file_item.title = title
        await session.commit()
        await session.refresh(file_item)
        return file_item


async def delete_file(file_id: str) -> None:
    async with async_session_maker() as session:
        await ServiceFactory.get_service(name="file", session=session).delete_file(file_id)


async def get_file_path(file_id: str) -> tuple[StoredFile, Path]:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="file", session=session).get_file_path(file_id)


async def create_alert(file_id: str, level: str, message: str) -> StoredFile:
    async with async_session_maker() as session:
        return await ServiceFactory.get_service(name="alert", session=session).create_alert(file_id, level, message)