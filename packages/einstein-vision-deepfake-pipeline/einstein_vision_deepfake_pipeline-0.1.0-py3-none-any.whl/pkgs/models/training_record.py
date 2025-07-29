from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime
from .enums import ImageDeepfakeLabel, RecordSourceType

class ImageDeepfakeTrainingRecord(BaseModel):
    # Compulsory
    image_path: str = Field(description="S3 object url")
    label: ImageDeepfakeLabel = Field(description="Label for deepfake classification fine tuning")
    id: UUID = Field(description="Unique ID of the training record")

    # Optional
    video_id: Optional[UUID] = Field(default=None, description="ID of the source video")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the record was created")
    source: Optional[RecordSourceType] = Field(default=None, description="source of the training record")
