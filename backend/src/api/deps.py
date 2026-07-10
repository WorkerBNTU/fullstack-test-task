from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.services.alert_service import AlertService
from src.services.file_service import FileService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_file_service(session: SessionDep) -> AsyncIterator[FileService]:
    yield FileService(session)


async def get_alert_service(session: SessionDep) -> AsyncIterator[AlertService]:
    yield AlertService(session)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]
