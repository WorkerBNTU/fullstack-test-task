from asgiref.sync import async_to_sync

from src.core.config import STORAGE_DIR, get_settings
from src.db.session import session_scope
from src.models import StoredFile
from src.services.alert_service import AlertService
from src.services.scanning import extract_metadata, scan_for_threats
from src.tasks.celery_app import celery_app

settings = get_settings()


async def _process_file(file_id: str) -> None:
    """Runs the scan -> extract-metadata -> alert pipeline for one file
    within a single DB session.

    Previously each stage was a separate Celery task that opened its own
    session and re-fetched the same row from Postgres (3 broker round-trips,
    3 sessions, 3 SELECTs per uploaded file). Business logic and end states
    are unchanged -- this only removes the redundant dispatch/fetch overhead
    between stages.
    """
    async with session_scope() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        # --- stage 1: threat scan ---
        file_item.processing_status = "processing"
        scan_result = scan_for_threats(
            original_name=file_item.original_name,
            size=file_item.size,
            mime_type=file_item.mime_type,
            settings=settings,
        )
        file_item.scan_status = scan_result.scan_status
        file_item.scan_details = scan_result.scan_details
        file_item.requires_attention = scan_result.requires_attention
        await session.commit()

        # --- stage 2: metadata extraction ---
        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
        else:
            file_item.metadata_json = extract_metadata(
                original_name=file_item.original_name,
                size=file_item.size,
                mime_type=file_item.mime_type,
                stored_path=stored_path,
            )
            file_item.processing_status = "processed"
        await session.commit()

        # --- stage 3: alert ---
        alert_service = AlertService(session)
        if file_item.processing_status == "failed":
            await alert_service.create_alert(file_id, "critical", "File processing failed")
        elif file_item.requires_attention:
            await alert_service.create_alert(
                file_id, "warning", f"File requires attention: {file_item.scan_details}"
            )
        else:
            await alert_service.create_alert(file_id, "info", "File processed successfully")


@celery_app.task(name="src.tasks.pipeline.process_file")
def process_file(file_id: str) -> None:
    async_to_sync(_process_file)(file_id)
