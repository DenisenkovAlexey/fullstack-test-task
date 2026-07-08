import logging
from pathlib import Path

from src.models import StoredFile

logger = logging.getLogger(__name__)


class MetadataService:
    """Сервис для извлечения метаданных файлов."""

    def extract_metadata(self, file_item: StoredFile, stored_path: Path) -> dict:
        metadata = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if not stored_path.exists():
            logger.warning("Stored file not found during metadata extraction: %s", stored_path)
            return metadata

        if file_item.mime_type.startswith("text/"):
            try:
                content = stored_path.read_text(encoding="utf-8", errors="ignore")
                metadata["line_count"] = len(content.splitlines())
                metadata["char_count"] = len(content)
            except Exception:
                logger.exception("Failed to read text file %s", stored_path)
        elif file_item.mime_type == "application/pdf":
            try:
                content = stored_path.read_bytes()
                metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)
            except Exception:
                logger.exception("Failed to read PDF file %s", stored_path)

        logger.info("Extracted metadata for file %s", file_item.id)
        return metadata
