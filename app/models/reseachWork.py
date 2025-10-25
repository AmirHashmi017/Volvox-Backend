from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

class ResearchModel(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)

    userId: Optional[str] = Field(alias="user_id", default=None)

    researchName: str
    fileName: str
    extension: str
    fileId: Optional[str] = Field(alias="file_id", default=None)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", "userId", "fileId", mode="before")
    @classmethod
    def _objectid_to_str(cls, v):
        if v is None:
            return v
        return str(v)
