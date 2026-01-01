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



