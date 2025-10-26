from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from app.schemas.researchWork import (
    ResearchResponse
)
from app.models.user import UserModel
from app.models.reseachWork import ResearchModel
from app.database import get_collection, get_gridfs_bucket
from app.config import settings
from app.middleware.auth import get_current_user
from datetime import datetime, timezone
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
    research_collection = await get_collection(settings.RESEARCH_COLLECTION)
    bucket = await get_gridfs_bucket()

    filename = file.filename or "upload"
    extension = (Path(filename).suffix or "").lstrip(".")
    content_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    grid_in = bucket.open_upload_stream(
        filename,
        metadata={
            "contentType": content_type,
            "userId": str(current_user.id),
            "extension": extension,
            "researchName": researchName,
        },
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
async def list_research(
    current_user: UserModel = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Search by researchName or fileName (case-insensitive)"),
    start: datetime | None = Query(None, description="Filter createdAt >= this ISO datetime"),
    end: datetime | None = Query(None, description="Filter createdAt <= this ISO datetime"),
):
    research_collection = await get_collection(settings.RESEARCH_COLLECTION)

    # Build base query
    query: dict = {"user_id": ObjectId(current_user.id)}

    # Search filter across researchName and fileName
    if search:
        query["$or"] = [
            {"researchName": {"$regex": search, "$options": "i"}},
            {"fileName": {"$regex": search, "$options": "i"}},
        ]

    # Time range filtering on createdAt
    created_filter: dict = {}
    if start:
        # Normalize to UTC if aware
        if start.tzinfo is not None:
            start = start.astimezone(timezone.utc).replace(tzinfo=None)
        created_filter["$gte"] = start
    if end:
        if end.tzinfo is not None:
            end = end.astimezone(timezone.utc).replace(tzinfo=None)
        created_filter["$lte"] = end
    if created_filter:
        query["createdAt"] = created_filter

    cursor = (
        research_collection
        .find(query)
        .sort("createdAt", -1) 
        .skip(offset)
        .limit(limit)
    )
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
    bucket = await get_gridfs_bucket()

    try:
        grid_out = await bucket.open_download_stream(ObjectId(file_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

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
