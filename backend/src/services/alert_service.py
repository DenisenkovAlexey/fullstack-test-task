import logging

from sqlalchemy import select

from src.models import Alert
from src.repositories.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class AlertService:
    """Сервис для управления алертами."""

    def __init__(self, alert_repo: AlertRepository) -> None:
        self._alert_repo = alert_repo

    async def list_alerts(self) -> list[Alert]:
        return list(await self._alert_repo.get_all())

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        # Идемпотентность: проверяем, существует ли уже такой алерт
        if await self._alert_repo.exists(file_id, level, message):
            logger.info("Alert already exists for file %s: %s", file_id, message)
            # Получаем существующий алерт
            result = await self._alert_repo._session.execute(
                select(Alert).where(
                    Alert.file_id == file_id,
                    Alert.level == level,
                    Alert.message == message,
                )
            )
            return result.scalar_one()

        alert = Alert(file_id=file_id, level=level, message=message)
        return await self._alert_repo.add(alert)

    async def send_file_alert(self, file_id: str, processing_status: str, requires_attention: bool, scan_details: str | None) -> None:
        if processing_status == "failed":
            level = "critical"
            message = "File processing failed"
        elif requires_attention:
            level = "warning"
            message = f"File requires attention: {scan_details}"
        else:
            level = "info"
            message = "File processed successfully"

        await self.create_alert(file_id, level, message)
