import asyncio
import logging

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.app import app_settings
from src.config.celery import celery_settings
from src.infrastructure.persistence.session import async_session_maker
from src.services.service_factory import ServiceFactory

logger = logging.getLogger(__name__)
_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


celery_app = Celery("file_tasks", broker=celery_settings.broker_url, backend=celery_settings.broker_url)


async def _scan_file_for_threats(file_id: str) -> None:
    async with async_session_maker() as session:
        file_service = ServiceFactory.get_service(name="file", session=session)
        scan_service = ServiceFactory.get_service(name="scan", session=session)
        file_item = await file_service.get_file(file_id)
        file_item.processing_status = "processing"
        await session.commit()

        scan_status, scan_details, requires_attention = scan_service.scan_file(file_item)
        file_item.scan_status = scan_status
        file_item.scan_details = scan_details
        file_item.requires_attention = requires_attention
        await session.commit()

    # Запускаем следующую задачу через celery_app.send_task для избежания циклического импорта
    celery_app.send_task("src.tasks.extract_file_metadata", args=[file_id])


async def _extract_file_metadata(file_id: str) -> None:
    async with async_session_maker() as session:
        file_service = ServiceFactory.get_service(name="file", session=session)
        metadata_service = ServiceFactory.get_service(name="metadata")
        file_item = await file_service.get_file(file_id)
        stored_path = app_settings.storage_dir / file_item.stored_name

        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await session.commit()
            celery_app.send_task("src.tasks.send_file_alert", args=[file_id])
            return

        metadata = metadata_service.extract_metadata(file_item, stored_path)
        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        await session.commit()

    celery_app.send_task("src.tasks.send_file_alert", args=[file_id])


async def _send_file_alert(file_id: str) -> None:
    async with async_session_maker() as session:
        alert_service = ServiceFactory.get_service(name="alert", session=session)
        file_service = ServiceFactory.get_service(name="file", session=session)
        file_item = await file_service.get_file(file_id)
        if not file_item:
            return
        await alert_service.send_file_alert(
            file_id=file_id,
            processing_status=file_item.processing_status,
            requires_attention=file_item.requires_attention,
            scan_details=file_item.scan_details,
        )


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scan_file_for_threats(self, file_id: str) -> None:
    try:
        run_in_worker_loop(_scan_file_for_threats(file_id))
    except Exception as exc:
        logger.error("scan_file_for_threats failed for %s: %s", file_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def extract_file_metadata(self, file_id: str) -> None:
    try:
        run_in_worker_loop(_extract_file_metadata(file_id))
    except Exception as exc:
        logger.error("extract_file_metadata failed for %s: %s", file_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_file_alert(self, file_id: str) -> None:
    try:
        run_in_worker_loop(_send_file_alert(file_id))
    except Exception as exc:
        logger.error("send_file_alert failed for %s: %s", file_id, exc)
        raise self.retry(exc=exc)
