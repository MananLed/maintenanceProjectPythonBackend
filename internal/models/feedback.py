from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


@dataclass
class Feedback:
    resident_id: str = field(metadata={"json": "resident_id"})
    flat: str = field(metadata={"json": "flat"})
    rating: int = field(metadata={"json": "rating"})
    content: str = field(metadata={"json": "content"})
    resident_name: str = field(metadata={"json": "name"})
    request_id: UUID = field(metadata={"json": "request_id"})
    assigned_to: str = field(metadata={"json": "assignedto"})
    service_type: str = field(metadata={"json": "servicetype"})
    date: str = field(metadata={"json": "date"})
    time_slot: str = field(metadata={"json": "timeslot"})
    id: UUID = field(metadata={"json": "id"}, default_factory=uuid4)


class FeedbackInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    rating: int = Field(min=1, max=5, alias="rating")
    content: str = Field(default="", alias="content")
    request_id: str = Field(alias="requestid")
