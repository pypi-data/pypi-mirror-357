from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


""" 
Labellers would label videos by assigning these labels
"""
class VideoDeepfakeLabel(str, Enum):
    REAL = "all_real_faces"
    DEEPFAKED = "all_deepfaked_faces"
    AI_GENERATED = "all_ai_generated_faces"
    MIXED = "mixed_real_and_ai_faces"
    UNSURE = "unsure"


""" 
After processing of videos into images/faces, they adopt these labels
"""
class ImageDeepfakeLabel(str, Enum):
    REAL = "real"
    DEEPFAKED = "deepfaked"
    AI_GENERATED = "ai_generated"

"""
where the record was obtained
"""
class RecordSourceType(str, Enum):
    SOCIAL_MEDIA_VIDEO = "social_media_video"
    DF40 = "df40"

