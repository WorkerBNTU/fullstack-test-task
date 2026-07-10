from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from src.api.deps import FileServiceDep
from src.schemas import FileItem, FileUpdate
from src.tasks.pipeline import process_file

router = APIRouter(tags=["files"])


@router.get("/files", response_model=list[FileItem])
async def list_files_view(service: FileServiceDep):
    return await service.list_files()


@router.post("/files", response_model=FileItem, status_code=201)
async def create_file_view(
    service: FileServiceDep,
    title: str = Form(...),
    file: UploadFile = File(...),
):
    file_item = await service.create_file(title=title, upload_file=file)
    process_file.delay(file_item.id)
    return file_item


@router.get("/files/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, service: FileServiceDep):
    return await service.get_file(file_id)


@router.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(file_id: str, payload: FileUpdate, service: FileServiceDep):
    return await service.update_file(file_id=file_id, title=payload.title)


@router.get("/files/{file_id}/download")
async def download_file(file_id: str, service: FileServiceDep):
    # get_file_path already validates the file exists on disk (404 otherwise)
    file_item, stored_path = await service.get_file_path(file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str, service: FileServiceDep):
    await service.delete_file(file_id)
