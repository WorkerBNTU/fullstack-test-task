from fastapi import APIRouter

from src.api.deps import AlertServiceDep
from src.schemas import AlertItem

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view(service: AlertServiceDep):
    return await service.list_alerts()
