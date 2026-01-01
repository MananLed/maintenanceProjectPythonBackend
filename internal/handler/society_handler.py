from fastapi import APIRouter, Request, HTTPException, Depends
from http import HTTPStatus
from internal.models.user import UserRole
from internal.dto.user import OfficerDetails
from internal.response.response import Response
from internal.utils.jwt import verify_jwt
from internal.service import society_service_instance
from internal.constants.constants import SERVER_ERROR



society_router = APIRouter(dependencies=[Depends(verify_jwt)])


@society_router.get("/society/residents")
def get_residents(request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        residents = society_service_instance.get_all_users_by_role(UserRole.ROLERESIDENT)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(residents, "Residents fetched successfully", HTTPStatus.OK)
    




@society_router.get("/society/officers")
def get_officers(request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        officers = society_service_instance.get_all_users_by_role(UserRole.ROLEOFFICER)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(officers, "Officers fetched successfully", HTTPStatus.OK)


@society_router.delete("/credentials/officer")
def delete_officer():
    pass


@society_router.delete("/credentials/resident")
def delete_resident():
    pass


@society_router.post("/officers")
def add_officer(officer_details_input: OfficerDetails):
    pass


@society_router.get("/society/residents/count")
def get_resident_count(request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        residents = society_service_instance.get_all_users_by_role(UserRole.ROLERESIDENT)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    residents_count = len(residents)
    
    return Response.success_response(residents_count, "Residents count fetched successfully", HTTPStatus.OK)


@society_router.get("/society/officers/count")
def get_officer_count(request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        officers = society_service_instance.get_all_users_by_role(UserRole.ROLEOFFICER)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    officers_count = len(officers)
    
    return Response.success_response(officers_count, "Officers count fetched successfully", HTTPStatus.OK)
