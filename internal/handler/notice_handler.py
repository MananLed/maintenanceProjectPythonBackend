from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Annotated
from http import HTTPStatus
from internal.dto.notice import NoticeInput
from internal.response.response import Response
from internal.models.user import UserRole
from internal.utils.jwt import verify_jwt
from internal.constants.constants import SERVER_ERROR
from internal.service import notice_service_instance

notice_router = APIRouter(dependencies=[Depends(verify_jwt)])


@notice_router.post("/notices/issue")
async def issue_notice(notice_input: NoticeInput, request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN and claims.get("role") != UserRole.ROLEOFFICER:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await notice_service_instance.issue_notice(notice_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Notice issued successfully", HTTPStatus.CREATED)
    


@notice_router.get("/notices")
async def get_all_notices():
    try:
        notices = await notice_service_instance.get_all_notices()
    except HTTPException as exception:
        print(exception)
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        print(exception)
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(notices, "Notices fetched successfully", HTTPStatus.OK)


@notice_router.get("/notices/month-year")
async def get_notices_by_month_year(year: Annotated[int, Query(gt=0)], month: Annotated[int | None, Query(gt=0, lt=13)] = None):
    try:
        notices = await notice_service_instance.get_all_notices_by_month_and_year(year, month)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(notices, "Notices fetched successfully", HTTPStatus.OK)
