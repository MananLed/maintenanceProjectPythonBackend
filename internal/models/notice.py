from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Notice:
    date_issued: datetime = field(metadata={"json": "date_issued"})
    content: str = field(metadata={"json": "content"})
    month: int = field(metadata={"json": "month"})
    year: int = field(metadata={"json": "year"})
    id: UUID = field(metadata={"json": "id"}, default_factory=uuid4)


class NoticeInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    content: str = Field(min_length=1, max_length=500, alias="content")
