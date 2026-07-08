from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.app import app_settings
from src.infrastructure.persistence.session import async_session_maker
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository
from src.services.alert_service import AlertService
from src.services.file_service import FileService
from src.services.metadata_service import MetadataService
from src.services.scan_service import ScanService

ServiceName = Literal["file", "scan", "metadata", "alert"]


class ServiceFactory:
    """Фабрика сервисов."""

    @staticmethod
    def get_service(name: ServiceName, session: AsyncSession | None = None):
        if name == "file":
            if session is None:
                raise ValueError("FileService requires a session")
            return FileService(
                file_repo=FileRepository(session),
                alert_repo=AlertRepository(session),
                storage_dir=app_settings.storage_dir,
            )
        if name == "scan":
            return ScanService()
        if name == "metadata":
            return MetadataService()
        if name == "alert":
            if session is None:
                raise ValueError("AlertService requires a session")
            return AlertService(alert_repo=AlertRepository(session))
        raise ValueError(f"Unknown service: {name}")


async def get_file_service() -> FileService:
    """Dependency для FastAPI."""
    async with async_session_maker() as session:
        yield ServiceFactory.get_service("file", session)


async def get_scan_service() -> ScanService:
    """Dependency для FastAPI."""
    yield ServiceFactory.get_service("scan")


async def get_metadata_service() -> MetadataService:
    """Dependency для FastAPI."""
    yield ServiceFactory.get_service("metadata")


async def get_alert_service() -> AlertService:
    """Dependency для FastAPI."""
    async with async_session_maker() as session:
        yield ServiceFactory.get_service("alert", session)
