from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import JSON

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    degree: str
    content: bytes
    prediction: Optional[List[str]] = Field(default=None, sa_type=JSON)