from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field

class PostInput(SQLModel):
    platform: str = "facebook"
    title: str
    description: str
    transcript: Optional[str] = ""
    links: List[str] = []

class Signals(SQLModel):
    clickbait: float = 0.0
    engagement_bait: float = 0.0
    misleading_thumb: float = 0.0
    low_quality_landing: float = 0.0
    repeat_offender_hint: float = 0.0

class Scores(SQLModel):
    risk_remove: float = 0.0
    risk_reduce: float = 0.0

class Actions(SQLModel):
    needs_inform: bool = False
    inform_block: str = ""

class Fixes(SQLModel):
    title: str = ""
    description: str = ""
    notes: List[str] = []

class Audit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    platform: str
    input_json: str
    output_json: str
