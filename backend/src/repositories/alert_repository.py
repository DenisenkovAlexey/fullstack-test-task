from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertRepository:
    """Репозиторий для работы с алертами."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, alert_id: int) -> Alert | None:
        return await self._session.get(Alert, alert_id)

    async def get_all(self) -> Sequence[Alert]:
        result = await self._session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_file_id(self, file_id: str) -> Sequence[Alert]:
        result = await self._session.execute(
            select(Alert).where(Alert.file_id == file_id).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def add(self, alert: Alert) -> Alert:
        self._session.add(alert)
        await self._session.commit()
        await self._session.refresh(alert)
        return alert

    async def delete(self, alert: Alert) -> None:
        await self._session.delete(alert)
        await self._session.commit()

    async def exists(self, file_id: str, level: str, message: str) -> bool:
        result = await self._session.execute(
            select(Alert.id).where(
                Alert.file_id == file_id,
                Alert.level == level,
                Alert.message == message,
            )
        )
        return result.scalar_one_or_none() is not None
