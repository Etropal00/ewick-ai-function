from pydantic import Field
from typing import List, Optional
from sqlmodel import SQLModel

class PostInput(SQLModel):
    platform: str = "facebook"
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(default="", max_length=1000)
    transcript: Optional[str] = ""
    links: List[str] = []
