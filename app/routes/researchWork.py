from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.schemas.researchWork import (
    ResearchResponse
)
from app.models.user import UserModel
from app.models.reseachWork import ResearchModel
from app.database import get_collection, get_gridfs_bucket
from app.config import settings
from app.middleware.auth import get_current_user
from datetime import datetime
from bson import ObjectId
from typing import List, AsyncGenerator
import mimetypes
from pathlib import Path

router = APIRouter(prefix="/research", tags=["Research"])

@router.post('/addResearch', response_model=ResearchResponse, status_code=status.HTTP_201_CREATED)
async def addResearch(
    researchName: str = Form(...),
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user)
):
    """Upload file to GridFS and create a research record."""
    research_collection = await get_collection(settings.RESEARCH_COLLECTION)
    bucket = await get_gridfs_bucket()

    filename = file.filename or "upload"
    extension = (Path(filename).suffix or "").lstrip(".")
    content_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    grid_in = await bucket.open_upload_stream(
        filename,
        metadata={
            "contentType": content_type,
            "userId": str(current_user.id),
            "extension": extension,
            "researchName": researchName,
        },
        content_type=content_type,
    )

    try:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await grid_in.write(chunk)
    finally:
        await grid_in.close()

    file_id = grid_in._id

    doc = {
        "user_id": ObjectId(current_user.id),
        "researchName": researchName,
        "fileName": filename,
        "extension": extension,
        "file_id": file_id,
        "createdAt": datetime.utcnow(),
    }

    result = await research_collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    model = ResearchModel(**doc)
    response = {
        **model.model_dump(by_alias=True),
        "fileUrl": f"{settings.API_V1_PREFIX}/research/file/{model.fileId}",
    }
    return response


@router.get("/", response_model=List[ResearchResponse])
async def list_research(current_user: UserModel = Depends(get_current_user)):
    """Return all research entries for the current user."""
    research_collection = await get_collection(settings.RESEARCH_COLLECTION)
    cursor = research_collection.find({"user_id": ObjectId(current_user.id)})
    items = []
    async for doc in cursor:
        model = ResearchModel(**doc)
        items.append({
            **model.model_dump(by_alias=True),
            "fileUrl": f"{settings.API_V1_PREFIX}/research/file/{model.fileId}",
        })
    return items


@router.get("/file/{file_id}")
async def download_file(file_id: str, current_user: UserModel = Depends(get_current_user)):
    """Stream a file from GridFS by file_id, ensuring owner access."""
    bucket = await get_gridfs_bucket()

    try:
        grid_out = await bucket.open_download_stream(ObjectId(file_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Optional access control: ensure the file belongs to the current user
    metadata = getattr(grid_out, "metadata", {}) or {}
    if metadata.get("userId") and metadata.get("userId") != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this file")

    async def file_iterator() -> AsyncGenerator[bytes, None]:
        while True:
            chunk = await grid_out.read(1024 * 1024)
            if not chunk:
                break
            yield chunk

    media_type = (metadata.get("contentType") if isinstance(metadata, dict) else None) or "application/octet-stream"
    headers = {"Content-Disposition": f"attachment; filename=\"{grid_out.filename}\""}
    return StreamingResponse(file_iterator(), media_type=media_type, headers=headers)
