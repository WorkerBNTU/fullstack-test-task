from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertRepository:
    """Pure data-access layer for ``Alert``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[Alert]:
        result = await self._session.execute(select(Alert).order_by(Alert.created_at.desc()))
        return list(result.scalars().all())

    async def add(self, alert: Alert) -> Alert:
        self._session.add(alert)
        await self._session.commit()
        await self._session.refresh(alert)
        return alert
