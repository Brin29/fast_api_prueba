from sqlmodel import SQLModel, Field
from typing import Optional

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    degree: str
    name: str