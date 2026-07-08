import asyncio
import logging
from pathlib import Path

import celery
# from aio_celery import Celery
from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config.celery import celery_settings
from src.config.database import database_settings
from src.models import Alert, StoredFile
from src.service import STORAGE_DIR

logger = logging.getLogger(__name__)
_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


celery_app = Celery("file_tasks", broker=celery_settings.broker_url, backend=celery_settings.broker_url)
# celery_app.conf.update(
#     broker_url=celery_settings.broker_url,
#     result_backend=celery_settings.broker_url,
# )
engine = create_async_engine(database_settings.url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def _scan_file_for_threats(file_id: str) -> None:
    async with async_session_maker() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        file_item.processing_status = "processing"
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
            reasons.append(f"suspicious extension {extension}")

        if file_item.size > 10 * 1024 * 1024:
            reasons.append("file is larger than 10 MB")

        if extension == ".pdf" and file_item.mime_type not in {"application/pdf", "application/octet-stream"}:
            reasons.append("pdf extension does not match mime type")

        file_item.scan_status = "suspicious" if reasons else "clean"
        file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
        file_item.requires_attention = bool(reasons)
        await session.commit()

    extract_file_metadata.delay(file_id)


async def _extract_file_metadata(file_id: str) -> None:
    async with async_session_maker() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await session.commit()
            send_file_alert.delay(file_id)
            return

        metadata = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if file_item.mime_type.startswith("text/"):
            content = stored_path.read_text(encoding="utf-8", errors="ignore")
            metadata["line_count"] = len(content.splitlines())
            metadata["char_count"] = len(content)
        elif file_item.mime_type == "application/pdf":
            content = stored_path.read_bytes()
            metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)

        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        await session.commit()

    send_file_alert.delay(file_id)


async def _send_file_alert(file_id: str) -> None:
    async with async_session_maker() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        if file_item.processing_status == "failed":
            level = "critical"
            message = "File processing failed"
        elif file_item.requires_attention:
            level = "warning"
            message = f"File requires attention: {file_item.scan_details}"
        else:
            level = "info"
            message = "File processed successfully"

        # Идемпотентность: проверяем, существует ли уже такой алерт
        existing = await session.execute(
            select(Alert).where(
                Alert.file_id == file_id,
                Alert.level == level,
                Alert.message == message,
            )
        )
        if existing.scalar_one_or_none():
            logger.info("Alert already exists for file %s: %s", file_id, message)
            return

        alert = Alert(file_id=file_id, level=level, message=message)
        session.add(alert)
        try:
            await session.commit()
        except Exception:
            logger.exception("Failed to create alert for file %s", file_id)
            raise


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
