from fastapi import APIRouter, Depends, Request, HTTPException, Query, Path
from http import HTTPStatus
from uuid import UUID
from typing import List, Annotated
from internal.dto.service_request import (
    ServiceRequestInput,
    RescheduleRequestInput,
    RequestProviderInput,
    DeleteUserRequestInput,
)
from internal.service import request_service_instance
from internal.models.service_request import ServiceType, Status, ServiceRequest
from internal.constants.constants import SERVER_ERROR
from internal.models.user import UserRole
from internal.response.response import Response
from internal.utils.jwt import verify_jwt

request_router = APIRouter(dependencies=[Depends(verify_jwt)])


@request_router.post("/service")
async def book_request(service_request_input: ServiceRequestInput, request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLERESIDENT:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await request_service_instance.book_service(service_request_input, claims)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        print(exception)
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Service request booked successfully", HTTPStatus.CREATED)


@request_router.delete("/service/cancel/{id}")
def delete_request(id):
    pass


@request_router.patch("/service/reschedule/{id}")
async def reschedule_request(id: Annotated[UUID, Path()], reschedule_request_input: RescheduleRequestInput, request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLERESIDENT:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await request_service_instance.reschedule_request(id, reschedule_request_input, claims)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Service request rescheduled successfully", HTTPStatus.OK)


@request_router.patch("/service/approve/{id}")
async def approve_request(id: Annotated[UUID, Path()], assigned_to_input: RequestProviderInput, request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN and claims.get("role") != UserRole.ROLEOFFICER:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await request_service_instance.update_request_status(Status.STATUSAPPROVED, id, assigned_to_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

    return Response.success_response(None, "Request approved successfully", HTTPStatus.OK)


@request_router.patch("/service/complete/{id}")
async def complete_request(id: Annotated[UUID, Path()], request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN and claims.get("role") != UserRole.ROLEOFFICER:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await request_service_instance.update_request_status(Status.STATUSCOMPLETED, id)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

    return Response.success_response(None, "Request marked completed successfully", HTTPStatus.OK)


@request_router.get("/service/all")
async def get_all_requests(request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN and claims.get("role") != UserRole.ROLEOFFICER:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        pending_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSPENDING)
        pending_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSPENDING)
        approved_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSAPPROVED)
        approved_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSAPPROVED)
        completed_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSCOMPLETED)
        completed_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSCOMPLETED)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    pending_request: List[ServiceRequest] = pending_request_1 + pending_request_2
    approved_request: List[ServiceRequest] = approved_request_1 + approved_request_2
    completed_request: List[ServiceRequest] = completed_request_1 + completed_request_2

    all_requests = {
        "Pending": pending_request,
        "Approved": approved_request,
        "Completed": completed_request
    }

    return Response.success_response(all_requests, "All requests fetched successfully", HTTPStatus.OK)


@request_router.get("/service/resident/all")
async def get_all_requests_of_resident(request: Request):
    claims = request.state.user 

    resident_id = claims.get("user_id")
    try:
        pending_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSPENDING, resident_id)
        pending_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSPENDING, resident_id)
        approved_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSAPPROVED, resident_id)
        approved_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSAPPROVED, resident_id)
        completed_request_1: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSCOMPLETED, resident_id)
        completed_request_2: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(ServiceType.ELECTRICIAN, Status.STATUSCOMPLETED, resident_id)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    pending_request: List[ServiceRequest] = pending_request_1 + pending_request_2
    approved_request: List[ServiceRequest] = approved_request_1 + approved_request_2
    completed_request: List[ServiceRequest] = completed_request_1 + completed_request_2

    all_requests = {
        "Pending": pending_request,
        "Approved": approved_request,
        "Completed": completed_request
    }

    return Response.success_response(all_requests, "All requests fetched successfully", HTTPStatus.OK)


@request_router.get("/service/type-status")
async def get_requests_by_type_status(status: Annotated[Status, Query()], serviceType: Annotated[ServiceType, Query()], request: Request):
    claims = request.state.user 

    try:
        if claims.get("role") == UserRole.ROLEADMIN or claims.get("role") == UserRole.ROLEOFFICER:
            requests: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(serviceType, status)
        else:
            requests: List[ServiceRequest] = await request_service_instance.get_requests_by_type_and_status(serviceType, status, claims.get("user_id"))
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(requests, "Requests fetched successfully", HTTPStatus.OK)


@request_router.get("/service/time-slots")
async def get_available_time_slots(serviceType: Annotated[ServiceType, Query()]): 
    try:
        available_slots = await request_service_instance.get_available_time_slots(serviceType)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

    return Response.success_response(available_slots, "Available time slots fetched successfully", HTTPStatus.OK)
    


def delete_requests_of_resident(user_id_input: DeleteUserRequestInput):
    pass
