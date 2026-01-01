from pydantic import BaseModel, Field
from enum import Enum


class ServiceType(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"


class ServiceRequestInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    slot_id: int = Field(alias="slotid")
    service_type: ServiceType = Field(alias="servicetype")


class RescheduleRequestInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    slot_id: int = Field(alias="slotid")


class RequestProviderInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    assigned_to: str = Field(alias="assignedto")


class DeleteUserRequestInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    user_id: str = Field(alias="userId")
