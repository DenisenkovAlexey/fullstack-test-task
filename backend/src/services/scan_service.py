import logging
from pathlib import Path

from src.models import StoredFile

logger = logging.getLogger(__name__)


class ScanService:
    """Сервис для сканирования файлов на угрозы."""

    def scan_file(self, file_item: StoredFile) -> tuple[str, str, bool]:
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
            reasons.append(f"suspicious extension {extension}")

        if file_item.size > 10 * 1024 * 1024:
            reasons.append("file is larger than 10 MB")

        if extension == ".pdf" and file_item.mime_type not in {"application/pdf", "application/octet-stream"}:
            reasons.append("pdf extension does not match mime type")

        scan_status = "suspicious" if reasons else "clean"
        scan_details = ", ".join(reasons) if reasons else "no threats found"
        requires_attention = bool(reasons)

        logger.info("Scanned file %s: %s", file_item.id, scan_status)
        return scan_status, scan_details, requires_attention
