from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum


class Status(str, Enum):
    STATUSPENDING = "pending"
    STATUSAPPROVED = "approved"
    STATUSCOMPLETED = "completed"


class ServiceType(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"


@dataclass
class ServiceRequest:
    resident_id: str = field(metadata={"json": "resident_id"})
    flat: str = field(metadata={"json": "flat"})
    time_slot: str = field(metadata={"json": "time_slot"})
    service_type: ServiceType = field(metadata={"json": "service_type"})
    date: str = field(metadata={"json": "date"})
    assigned_to: str = field(metadata={"json": "assignedto"})
    feedback_given: bool = field(metadata={"json": "feedbackgiven"})
    status: Status = field(metadata={"json": "status"}, default=Status.STATUSPENDING)
    request_id: UUID = field(metadata={"json": "request_id"}, default_factory=uuid4)
