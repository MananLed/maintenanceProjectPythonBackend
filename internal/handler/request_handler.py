from fastapi import APIRouter
from internal.dto.service_request import (
    ServiceRequestInput,
    RescheduleRequestInput,
    RequestProviderInput,
    DeleteUserRequestInput,
)

request_router = APIRouter()


@request_router.post("/service")
def book_request(service_request_input: ServiceRequestInput):
    pass


@request_router.delete("/service/cancel/{id}")
def delete_request(id):
    pass


@request_router.patch("/service/reschedule/{id}")
def reschedule_request(id, reschedule_request_input: RescheduleRequestInput):
    pass


@request_router.patch("/service/approve/{id}")
def approve_request(id, assigned_to_input: RequestProviderInput):
    pass


@request_router.patch("/service/complete/{id}")
def complete_request(id):
    pass


@request_router.get("/service/all")
def get_all_requests():
    pass


@request_router.get("/service/resident/all")
def get_all_requests_of_resident():
    pass


@request_router.get("service/type-status")
def get_requests_by_type_status():
    pass


@request_router.get("/service/time-slots")
def get_available_time_slots():
    pass


def delete_requests_of_resident(user_id_input: DeleteUserRequestInput):
    pass
