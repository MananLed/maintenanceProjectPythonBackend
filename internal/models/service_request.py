from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class Status(str, Enum):
    STATUSPENDING = "pending"
    STATUSAPPROVED = "approved"
    STATUSCOMPLETED = "completed"


class ServiceType(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"

class ServiceRequest(BaseModel):
    resident_id: str = Field(alias="resident_id")
    flat: str = Field(alias="flat")
    time_slot: str = Field(alias="time_slot")
    service_type: ServiceType = Field(alias="service_type")
    date: str = Field(alias="date")
    assigned_to: str = Field(alias="assignedto", default="")
    feedback_given: bool = Field(alias="feedbackgiven", default=False)
    status: Status = Field(alias="status", default=Status.STATUSPENDING)
    request_id: UUID = Field(alias="request_id", default_factory=uuid4)

