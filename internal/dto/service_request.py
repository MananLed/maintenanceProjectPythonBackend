from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ServiceType(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"


class ServiceRequestInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    slot_id: int = Field(alias="slotid", ge=0, lt=1000)
    service_type: ServiceType = Field(alias="servicetype")


class RescheduleRequestInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    slot_id: int = Field(alias="slotid", ge=0, lt=1000)


class RequestProviderInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    assigned_to: str = Field(alias="assignedto", max_length=26)


class DeleteUserRequestInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    user_id: str = Field(alias="userId", max_length=1000)
