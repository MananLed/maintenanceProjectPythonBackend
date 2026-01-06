from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Feedback(BaseModel):
    resident_id: str = Field(alias="resident_id")
    flat: str = Field(alias="flat")
    rating: int = Field(alias="rating")
    content: str = Field(alias="content")
    resident_name: str = Field(alias="name")
    request_id: UUID = Field(alias="request_id")
    assigned_to: str = Field(alias="assignedto")
    service_type: str = Field(alias="servicetype")
    date: str = Field(alias="date")
    time_slot: str = Field(alias="timeslot")
    id: UUID = Field(alias="id", default_factory=uuid4)

