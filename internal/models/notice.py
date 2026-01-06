from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Notice(BaseModel):
    date_issued: str = Field(alias="date_issued")
    content: str = Field(alias="content")
    month: int = Field(alias="month")
    year: int = Field(alias="year")
    id: UUID = Field(alias="id", default_factory=uuid4)

